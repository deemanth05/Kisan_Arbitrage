import asyncio
import sys
import io

# Ensure UTF-8 output encoding for console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from backend.app.services.arbitrage_engine import arbitrage_engine
from backend.app.services.spoilage_engine import spoilage_engine
from backend.app.services.logistics_engine import logistics_engine
from backend.app.services.msp_engine import msp_engine
from backend.app.scrapers.fuel_scraper import fuel_scraper
from backend.app.scrapers.mandi_scraper import mandi_scraper
from backend.app.db.mandi_master import find_nearby_mandis
from backend.app.models.schemas import AnalysisRequest

async def run_real_world_verification():
    print("=================================================================")
    print("      KISANARBITRAGE: REAL-WORLD GROUND TRUTH VALIDATION         ")
    print("=================================================================\n")

    # 1. Verify Live Diesel Prices
    print("--- 1. FUEL ECONOMICS VERIFICATION ---")
    districts = ["kolhapur", "pune", "mumbai", "belgaum"]
    for d in districts:
        price = await fuel_scraper.get_diesel_price(d)
        print(f"  • {d.capitalize()} District Diesel Price: Rs. {price:.2f} / Litre")

    # 2. Verify Statutory MSP & Operation Greens Benchmarks
    print("\n--- 2. STATUTORY BENCHMARKS VERIFICATION ---")
    crops_to_check = [
        ("Soybean", 4650.0),
        ("Cotton", 7200.0),
        ("Wheat", 2700.0),
        ("Tomato", 1850.0),
        ("Onion", 2400.0)
    ]
    for crop, sample_rate in crops_to_check:
        bench = msp_engine.evaluate_benchmark(crop, sample_rate)
        print(f"  • {crop}: Market Rs. {sample_rate:.0f} vs {bench['benchmark_name']} Rs. {bench['benchmark_price']:.0f} -> Status: {bench['benchmark_status']} ({bench['badge_text']})")

    # 3. Verify ICAR Spoilage Curves with Route Temperatures
    print("\n--- 3. ICAR POST-HARVEST SPOILAGE VERIFICATION ---")
    # Perishable Tomato in Heat
    loss_tom_heat, pct_tom_heat = spoilage_engine.calculate_spoilage("tomato", 40000.0, 4.5, 36.0, False)
    # Perishable Tomato in Rain
    loss_tom_rain, pct_tom_rain = spoilage_engine.calculate_spoilage("tomato", 40000.0, 4.5, 28.0, True)
    # Non-Perishable Soybean in Heat
    loss_soy, pct_soy = spoilage_engine.calculate_spoilage("soybean", 80000.0, 4.5, 36.0, False)

    print(f"  • Tomato (4.5 hrs @ 36°C): Spoilage = {pct_tom_heat:.2f}% (Rs. {loss_tom_heat:.0f} loss)")
    print(f"  • Tomato (4.5 hrs @ 28°C + Rain): Spoilage = {pct_tom_rain:.2f}% (Rs. {loss_tom_rain:.0f} loss)")
    print(f"  • Soybean (4.5 hrs @ 36°C): Spoilage = {pct_soy:.2f}% (Rs. {loss_soy:.0f} loss)")

    # 4. End-to-End Real Arbitrage Execution: 20 Quintals Tomato from Kolhapur
    print("\n--- 4. FULL ARBITRAGE CALCULATION: 20 QTL TOMATO FROM KOLHAPUR ---")
    req = AnalysisRequest(
        commodity="Tomato",
        quantity=20.0,
        unit="quintal",
        origin_city="Kolhapur",
        origin_lat=16.6913,
        origin_lon=74.2432,
        vehicle_type="bolero_pickup"
    )
    candidate_mandis = find_nearby_mandis(req.origin_lat, req.origin_lon, radius_km=260.0, limit=5)
    result = await arbitrage_engine.compute_arbitrage("sess_verify_1", req, candidate_mandis)

    rec = result.recommended_mandi
    print(f"\nRecommended Top Mandi: {rec.mandi_name} ({rec.distance_km:.1f} km)")
    print(f"  • Modal Price: Rs. {rec.modal_price:.0f}/quintal")
    print(f"  • Gross Produce Value: Rs. {rec.breakdown.gross_revenue:.0f}")
    print(f"  • Road Freight: -Rs. {rec.breakdown.freight_cost:.0f}")
    print(f"  • APMC Statutory Cess ({rec.breakdown.apmc_cess_percentage}%): -Rs. {rec.breakdown.apmc_cess:.0f}")
    print(f"  • Hamali/Weighment: -Rs. {rec.breakdown.weighment_loading:.0f}")
    print(f"  • Spoilage Loss ({rec.breakdown.spoilage_percentage}% @ {rec.breakdown.transit_temperature:.1f}°C): -Rs. {rec.breakdown.spoilage_loss_amount:.0f}")
    print(f"  • NET PROFIT: Rs. {rec.breakdown.net_profit:.0f}")
    print(f"  • NET GAIN OVER LOCAL MANDI: +Rs. {rec.breakdown.profit_difference_vs_local:.0f}")
    print(f"  • Best Time to Sell: {result.best_time_to_sell} ({result.prediction_rationale})")
    print(f"  • Localized Advice: \"{result.localized_explanation}\"")

    print("\nAlternative Mandis Evaluated:")
    for alt in result.alternative_mandis:
        print(f"  - {alt.mandi_name} ({alt.distance_km:.1f} km): Modal Rs. {alt.modal_price:.0f}/q | Net Profit: Rs. {alt.breakdown.net_profit:.0f} (Diff: Rs. {alt.breakdown.profit_difference_vs_local:.0f})")

if __name__ == "__main__":
    asyncio.run(run_real_world_verification())
