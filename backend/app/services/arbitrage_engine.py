import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from backend.app.models.schemas import (
    AnalysisRequest,
    ArbitrageAnalysisResult,
    MandiArbitrageOption,
    MandiCostBreakdown,
    SchemeCard
)
from backend.app.scrapers.mandi_scraper import mandi_scraper
from backend.app.services.logistics_engine import logistics_engine
from backend.app.services.spoilage_engine import spoilage_engine
from backend.app.services.msp_engine import msp_engine
from backend.app.services.scheme_engine import scheme_engine
from backend.app.db.database import AsyncSessionLocal, DBCommunityReport
from sqlalchemy import select, desc

logger = logging.getLogger(__name__)

class ArbitrageEngine:
    """
    Core Deterministic Financial and Perishability Arbitrage Engine.
    
    Data Integrity & Mathematical Rules:
    1. Zero arithmetic hallucinations: executed in 100% native Python floating point.
    2. Formula: Gross Produce Value - (Road Freight + Statutory APMC Cess + Hamali/Loading + ICAR Spoilage Decay)
    3. Transparent Data Provenance for every single rate, distance, and temperature reading.
    4. Honest reporting: No fake numbers served when market data is unavailable.
    """

    async def compute_arbitrage(
        self,
        session_id: str,
        request: AnalysisRequest,
        candidate_mandis: List[Dict[str, Any]]
    ) -> ArbitrageAnalysisResult:
        commodity = request.commodity.strip().capitalize()
        quantity = float(request.quantity)
        origin_lat = float(request.origin_lat)
        origin_lon = float(request.origin_lon)
        vehicle_type = request.vehicle_type

        # 1. Fetch live community ground truth reports for this commodity
        community_prices: Dict[str, Tuple[float, str]] = {}
        async with AsyncSessionLocal() as session:
            stmt = select(DBCommunityReport).where(
                DBCommunityReport.commodity.ilike(f"%{commodity[:4]}%")
            ).order_by(desc(DBCommunityReport.created_at))
            reports = (await session.execute(stmt)).scalars().all()
            for r in reports:
                if r.mandi_id not in community_prices:
                    community_prices[r.mandi_id] = (r.price_received, r.created_at.strftime("%d %b, %H:%M"))

        # 2. Parallel evaluation of all candidate mandis
        evaluated_options: List[MandiArbitrageOption] = []
        local_baseline_option: Optional[MandiArbitrageOption] = None

        for mandi in candidate_mandis:
            m_id = mandi["id"]
            m_name = mandi["name"]
            m_dist_name = mandi["district"]
            m_state = mandi["state"]
            m_lat = mandi["lat"]
            m_lon = mandi["lon"]
            m_cess_pct = float(mandi.get("apmc_cess_percentage", 1.05))

            # Fetch authentic market rates
            rates_info = await mandi_scraper.get_mandi_rates(
                mandi_name=m_name,
                district=m_dist_name,
                state=m_state,
                commodity=commodity
            )

            # Compute real turn-by-turn road logistics
            freight_info = await logistics_engine.calculate_freight_cost(
                origin_lat=origin_lat,
                origin_lon=origin_lon,
                dest_lat=m_lat,
                dest_lon=m_lon,
                dest_district=m_dist_name,
                dest_state=m_state,
                vehicle_type=vehicle_type
            )

            # Compute live transit weather along route
            mid_lat = (origin_lat + m_lat) / 2.0
            mid_lon = (origin_lon + m_lon) / 2.0
            weather_info = await spoilage_engine.get_route_weather(mid_lat, mid_lon)

            # Modal price & financial math
            modal_price = float(rates_info["modal_price"])
            min_price = float(rates_info["min_price"])
            max_price = float(rates_info["max_price"])

            gross_revenue = quantity * modal_price
            freight_cost = float(freight_info["freight_cost"])
            distance_km = float(freight_info["distance_km"])
            dur_hrs = float(freight_info["transit_duration_hours"])
            
            # APMC statutory cess on gross value
            apmc_cess = gross_revenue * (m_cess_pct / 100.0)

            # Hamali & weighment: standard ₹15/quintal
            weighment_loading = quantity * 15.0

            # ICAR-CIPHET spoilage loss
            spoilage_loss, spoilage_pct = spoilage_engine.calculate_spoilage(
                commodity=commodity,
                gross_value=gross_revenue,
                transit_duration_hours=dur_hrs,
                ambient_temperature=weather_info["temperature_celsius"],
                has_rain=weather_info["has_rain"]
            )

            # Net Profit
            net_profit = gross_revenue - (freight_cost + apmc_cess + weighment_loading + spoilage_loss)

            # Benchmark evaluation (MSP or TOP Operation Greens)
            bench_eval = msp_engine.evaluate_benchmark(commodity, modal_price)

            # Cost Breakdown model
            breakdown = MandiCostBreakdown(
                gross_revenue=round(gross_revenue, 2),
                freight_cost=round(freight_cost, 2),
                diesel_price_per_litre=freight_info["diesel_price_per_litre"],
                distance_km=distance_km,
                transit_duration_hours=dur_hrs,
                apmc_cess=round(apmc_cess, 2),
                apmc_cess_percentage=m_cess_pct,
                weighment_loading=round(weighment_loading, 2),
                spoilage_loss_amount=round(spoilage_loss, 2),
                spoilage_percentage=spoilage_pct,
                transit_temperature=weather_info["temperature_celsius"],
                has_rain=weather_info["has_rain"],
                net_profit=round(net_profit, 2),
                profit_difference_vs_local=0.0,
                routing_source=freight_info["routing_source"],
                weather_source=weather_info["data_source"]
            )

            comm_rep_price, comm_rep_time = community_prices.get(m_id, (None, None))

            opt = MandiArbitrageOption(
                mandi_id=m_id,
                mandi_name=m_name,
                district=m_dist_name,
                state=m_state,
                lat=m_lat,
                lon=m_lon,
                distance_km=distance_km,
                modal_price=modal_price,
                min_price=min_price,
                max_price=max_price,
                is_recommended=False,
                is_local_baseline=(distance_km < 1.0),
                benchmark_status=bench_eval["benchmark_status"],
                benchmark_name=bench_eval["benchmark_name"],
                benchmark_diff=bench_eval["benchmark_diff"],
                market_pulse=rates_info["market_pulse"],
                arrival_quantity=rates_info["arrival_quantity"],
                arrival_date=rates_info.get("arrival_date", ""),
                trend_direction=rates_info["trend_direction"],
                sparkline_prices=rates_info["sparkline_prices"],
                community_reported_price=comm_rep_price,
                community_report_time=comm_rep_time,
                data_source=rates_info["data_source"],
                data_provenance=rates_info["data_provenance"],
                is_live_data=rates_info["is_live"],
                data_available=rates_info["data_available"],
                breakdown=breakdown
            )

            if distance_km < 1.0 or not local_baseline_option:
                local_baseline_option = opt

            evaluated_options.append(opt)

        # 3. Compute Net Profit Difference vs Local Baseline
        baseline_net = local_baseline_option.breakdown.net_profit if local_baseline_option else 0.0
        for opt in evaluated_options:
            diff = opt.breakdown.net_profit - baseline_net
            opt.breakdown.profit_difference_vs_local = round(diff, 2)

        # 4. Rank Options: Highest Net Profit first (filtering out mandis with zero price data if possible)
        evaluated_options.sort(key=lambda o: (o.data_available, o.breakdown.net_profit), reverse=True)
        
        recommended_mandi = evaluated_options[0] if evaluated_options else local_baseline_option
        if recommended_mandi:
            recommended_mandi.is_recommended = True

        alternative_mandis = evaluated_options[1:] if len(evaluated_options) > 1 else []

        # 5. Predictive "Best Time to Sell" Intelligence
        best_time, rationale = self._predict_best_time(
            commodity=commodity,
            recommended_option=recommended_mandi,
            local_option=local_baseline_option
        )

        # 6. Indic Localized Explanation
        localized_text = self._generate_localized_explanation(
            commodity=commodity,
            quantity=quantity,
            unit=request.unit,
            rec=recommended_mandi,
            local=local_baseline_option
        )

        # 7. Evaluate Government Schemes
        eligible_schemes = scheme_engine.evaluate_schemes(
            commodity=commodity,
            state=request.origin_city,
            distance_km=recommended_mandi.distance_km if recommended_mandi else 0.0
        )

        return ArbitrageAnalysisResult(
            session_id=session_id,
            commodity=commodity,
            quantity=quantity,
            unit=request.unit,
            origin_city=request.origin_city,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            vehicle_type=vehicle_type,
            recommended_mandi=recommended_mandi,
            alternative_mandis=alternative_mandis,
            best_time_to_sell=best_time,
            prediction_rationale=rationale,
            localized_explanation=localized_text,
            eligible_schemes=eligible_schemes,
            created_at=datetime.utcnow().isoformat()
        )

    def _predict_best_time(
        self,
        commodity: str,
        recommended_option: MandiArbitrageOption,
        local_option: Optional[MandiArbitrageOption]
    ) -> Tuple[str, str]:
        comm_lower = commodity.lower()
        is_perishable = comm_lower in ["tomato", "brinjal", "bhindi", "cauliflower", "green chilli"]
        
        if is_perishable:
            temp = recommended_option.breakdown.transit_temperature
            if temp > 32.0 or recommended_option.breakdown.has_rain:
                return (
                    "SELL_TODAY",
                    f"Perishable {commodity} faces {recommended_option.breakdown.spoilage_percentage}% transit loss under {temp:.1f}°C heat. Dispatch immediately to lock in maximum take-home profit."
                )
            else:
                return (
                    "SELL_TODAY",
                    f"Immediate dispatch to {recommended_option.mandi_name} maximizes take-home profit of ₹{recommended_option.breakdown.net_profit:,.0f} (+₹{recommended_option.breakdown.profit_difference_vs_local:,.0f} over local market)."
                )
        else:
            # Grains / Oilseeds / Onions
            if recommended_option.trend_direction == "UP":
                return (
                    "WAIT_2_3_DAYS",
                    f"Prices at {recommended_option.mandi_name} are trending upward. Holding non-perishable {commodity} for 2-3 days could yield higher returns."
                )
            return (
                "SELL_TODAY",
                f"Favorable selling conditions today at {recommended_option.mandi_name} with ₹{recommended_option.modal_price:,.0f}/q modal rate."
            )

    def _generate_localized_explanation(
        self,
        commodity: str,
        quantity: float,
        unit: str,
        rec: MandiArbitrageOption,
        local: Optional[MandiArbitrageOption]
    ) -> str:
        diff = rec.breakdown.profit_difference_vs_local
        if diff > 100.0:
            return (
                f"किसान मित्र, आपके {quantity} {unit} {commodity} के लिए सबसे लाभदायक मंडी {rec.mandi_name} है। "
                f"यहाँ बेचने पर आपको कुल ₹{rec.breakdown.net_profit:,.0f} का शुद्ध मुनाफा होगा, जो स्थानीय मंडी से ₹{diff:,.0f} अधिक है।"
            )
        else:
            return (
                f"किसान मित्र, आपके {quantity} {unit} {commodity} के लिए {rec.mandi_name} सबसे उपयुक्त है। "
                f"यहाँ बेचने पर कुल ₹{rec.breakdown.net_profit:,.0f} का शुद्ध लाभ मिलेगा।"
            )

arbitrage_engine = ArbitrageEngine()
