import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
from backend.app.models.schemas import (
    AnalysisRequest,
    MandiArbitrageOption,
    MandiCostBreakdown,
    ArbitrageAnalysisResult,
    SchemeCard
)
from backend.app.scrapers.mandi_scraper import mandi_scraper
from backend.app.services.logistics_engine import logistics_engine
from backend.app.services.spoilage_engine import spoilage_engine
from backend.app.services.msp_engine import msp_engine
from backend.app.services.scheme_engine import scheme_engine

logger = logging.getLogger(__name__)

# Statutory APMC Cess & Market Fees per State
APMC_CESS_RATES = {
    "maharashtra": 1.05,  # 1.05% market fee
    "karnataka": 1.00,    # 1.0% market fee
    "default": 1.05
}

class ArbitrageEngine:
    """
    Core deterministic arbitrage calculation engine.
    Calculates true net profitability, ranks mandis against the local baseline,
    and produces verified financial breakdowns.
    """
    
    async def evaluate_mandi_option(
        self,
        mandi_info: Dict[str, Any],
        origin_city: str,
        origin_lat: float,
        origin_lon: float,
        commodity: str,
        quantity_quintals: float,
        vehicle_type: str
    ) -> MandiArbitrageOption:
        mandi_id = mandi_info["id"]
        mandi_name = mandi_info["name"]
        district = mandi_info.get("district", origin_city)
        state = mandi_info.get("state", "Maharashtra").lower()
        dest_lat = mandi_info["lat"]
        dest_lon = mandi_info["lon"]
        
        # 1. Scrape / Retrieve Real-Time Prices & Arrivals
        rates = await mandi_scraper.get_mandi_rates(commodity, mandi_name, district)
        modal_price = rates["modal_price"]
        gross_revenue = round(quantity_quintals * modal_price, 2)
        
        # 2. Road Routing & Real Freight Calculation
        distance_km, duration_hrs = await logistics_engine.get_route_matrix(
            origin_lat, origin_lon, dest_lat, dest_lon
        )
        freight_cost, diesel_price, tolls = await logistics_engine.calculate_freight(
            origin_city, distance_km, vehicle_type
        )
        
        # 3. APMC Market Fee / Cess & Hamali (Loading/Weighment)
        cess_pct = APMC_CESS_RATES.get(state, APMC_CESS_RATES["default"])
        apmc_cess_amount = round(gross_revenue * (cess_pct / 100.0), 2)
        weighment_loading = round(quantity_quintals * 15.0, 2)  # Standard ₹15/quintal
        
        # 4. Route Weather & ICAR Spoilage Model
        route_temp, has_rain = await spoilage_engine.fetch_route_weather(
            (origin_lat + dest_lat) / 2.0,
            (origin_lon + dest_lon) / 2.0
        )
        spoilage_loss, spoilage_pct = spoilage_engine.calculate_spoilage(
            commodity, gross_revenue, duration_hrs, route_temp, has_rain
        )
        
        # 5. Net Projected Profit
        total_deductions = freight_cost + apmc_cess_amount + weighment_loading + spoilage_loss
        net_profit = round(gross_revenue - total_deductions, 2)
        
        # 6. Benchmark Evaluation (MSP / TOP Benchmark)
        bench = msp_engine.evaluate_benchmark(commodity, modal_price)
        
        cost_breakdown = MandiCostBreakdown(
            gross_revenue=gross_revenue,
            freight_cost=freight_cost,
            diesel_price_per_litre=diesel_price,
            distance_km=distance_km,
            transit_duration_hours=duration_hrs,
            apmc_cess=apmc_cess_amount,
            apmc_cess_percentage=cess_pct,
            weighment_loading=weighment_loading,
            spoilage_loss_amount=spoilage_loss,
            spoilage_percentage=spoilage_pct,
            transit_temperature=route_temp,
            has_rain=has_rain,
            net_profit=net_profit,
            profit_difference_vs_local=0.0  # Populated after ranking
        )
        
        return MandiArbitrageOption(
            mandi_id=mandi_id,
            mandi_name=mandi_name,
            district=district,
            state=mandi_info.get("state", "Maharashtra"),
            lat=dest_lat,
            lon=dest_lon,
            distance_km=distance_km,
            modal_price=modal_price,
            min_price=rates["min_price"],
            max_price=rates["max_price"],
            price_unit="₹/quintal",
            is_recommended=False,
            is_local_baseline=(distance_km <= 5.0),
            benchmark_status=bench["benchmark_status"],
            benchmark_name=bench["benchmark_name"],
            benchmark_diff=bench["benchmark_diff"],
            market_pulse=rates["market_pulse"],
            arrival_quantity=rates["arrival_quantity"],
            arrival_unit=rates["arrival_unit"],
            trend_direction=rates["trend_direction"],
            sparkline_prices=rates["sparkline_prices"],
            breakdown=cost_breakdown
        )

    async def compute_arbitrage(
        self,
        session_id: str,
        request: AnalysisRequest,
        candidate_mandis: List[Dict[str, Any]]
    ) -> ArbitrageAnalysisResult:
        """
        Evaluates all candidate mandis, calculates net profits, ranks them,
        and formulates the predictive intelligence recommendation.
        """
        # Convert quantity to quintals if needed
        qty_quintals = request.quantity
        if request.unit.lower() in ["ton", "tonne", "tons", "tonnes"]:
            qty_quintals = request.quantity * 10.0
        elif request.unit.lower() in ["kg", "kgs", "kilogram"]:
            qty_quintals = request.quantity / 100.0
            
        evaluated_options: List[MandiArbitrageOption] = []
        for m in candidate_mandis:
            option = await self.evaluate_mandi_option(
                mandi_info=m,
                origin_city=request.origin_city,
                origin_lat=request.origin_lat,
                origin_lon=request.origin_lon,
                commodity=request.commodity,
                quantity_quintals=qty_quintals,
                vehicle_type=request.vehicle_type
            )
            evaluated_options.append(option)
            
        # Find or establish local baseline
        local_baseline = next((opt for opt in evaluated_options if opt.is_local_baseline), None)
        if not local_baseline and evaluated_options:
            # Closest mandi is local baseline
            local_baseline = min(evaluated_options, key=lambda x: x.distance_km)
            local_baseline.is_local_baseline = True
            
        baseline_profit = local_baseline.breakdown.net_profit if local_baseline else 0.0
        
        # Sort options by Net Profit descending
        evaluated_options.sort(key=lambda x: x.breakdown.net_profit, reverse=True)
        
        # Calculate profit difference vs local baseline and mark recommended
        for i, opt in enumerate(evaluated_options):
            opt.breakdown.profit_difference_vs_local = round(opt.breakdown.net_profit - baseline_profit, 2)
            if i == 0:
                opt.is_recommended = True
                
        recommended = evaluated_options[0]
        alternatives = evaluated_options[1:] if len(evaluated_options) > 1 else []
        
        # Predictive "Best Time to Sell" Logic
        # If route temperature is high and produce is perishable -> SELL TODAY
        # If trend is UP and spoilage is low -> WAIT 2-3 DAYS
        is_perishable = request.commodity.lower() in ["tomato", "green_chilli"]
        high_heat = recommended.breakdown.transit_temperature >= 35.0
        
        if is_perishable and high_heat:
            best_time = "SELL_TODAY"
            rationale = (
                f"Sell Today at {recommended.mandi_name}. Ambient route temperature is "
                f"{recommended.breakdown.transit_temperature}°C with high spoilage risk if delayed."
            )
        elif recommended.trend_direction == "UP" and not is_perishable:
            best_time = "WAIT_2_3_DAYS"
            rationale = (
                f"Prices at {recommended.mandi_name} are trending upward (+{int(recommended.benchmark_diff)} vs benchmark). "
                f"Holding non-perishable {request.commodity} for 2-3 days could yield higher returns."
            )
        else:
            best_time = "SELL_TODAY"
            rationale = (
                f"Immediate dispatch to {recommended.mandi_name} maximizes take-home profit of "
                f"₹{int(recommended.breakdown.net_profit):,} (+₹{int(recommended.breakdown.profit_difference_vs_local):,} over local market)."
            )
            
        # Localized Hindi / Indic Summary Explanation
        net_diff = int(recommended.breakdown.profit_difference_vs_local)
        localized_text = (
            f"किसान मित्र, आपके {request.quantity} {request.unit} {request.commodity} के लिए सबसे लाभदायक मंडी "
            f"{recommended.mandi_name} है। यहाँ बेचने पर आपको कुल ₹{int(recommended.breakdown.net_profit):,} "
            f"का शुद्ध मुनाफा होगा, जो स्थानीय मंडी से ₹{abs(net_diff):,} {'अधिक' if net_diff >= 0 else 'कम'} है।"
        )
        
        schemes = scheme_engine.get_eligible_schemes(request.commodity)
        
        return ArbitrageAnalysisResult(
            session_id=session_id,
            commodity=request.commodity,
            quantity=request.quantity,
            unit=request.unit,
            origin_city=request.origin_city,
            origin_lat=request.origin_lat,
            origin_lon=request.origin_lon,
            vehicle_type=request.vehicle_type,
            recommended_mandi=recommended,
            alternative_mandis=alternatives,
            best_time_to_sell=best_time,
            prediction_rationale=rationale,
            localized_explanation=localized_text,
            eligible_schemes=schemes,
            created_at=datetime.utcnow().isoformat()
        )

arbitrage_engine = ArbitrageEngine()
