import asyncio
import argparse
import sys
import io

# Ensure UTF-8 output encoding for console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from backend.app.services.arbitrage_engine import arbitrage_engine
from backend.app.db.mandi_master import find_nearby_mandis
from backend.app.models.schemas import AnalysisRequest

async def run_cli(crop: str, qty: float, unit: str, origin: str, lat: float, lon: float, vehicle: str):
    print("\n" + "="*65)
    print(f"🌾 KISANARBITRAGE: Autonomous Mandi Arbitrage Engine")
    print("="*65)
    print(f"Query: {qty} {unit} of {crop} from {origin} ({lat}, {lon})")
    print(f"Vehicle: {vehicle}\n")
    print("🔍 Discovering nearby candidate APMC mandis within 260km radius...")
    
    candidate_mandis = find_nearby_mandis(lat, lon, radius_km=260.0, limit=5)
    print(f"✅ Found {len(candidate_mandis)} candidate mandis.")
    print("⚙️ Executing deterministic Net Profit & ICAR Spoilage calculation...\n")
    
    req = AnalysisRequest(
        commodity=crop,
        quantity=qty,
        unit=unit,
        origin_city=origin,
        origin_lat=lat,
        origin_lon=lon,
        vehicle_type=vehicle
    )
    
    result = await arbitrage_engine.compute_arbitrage("cli_session", req, candidate_mandis)
    rec = result.recommended_mandi

    print("🏆" + "-"*63)
    print(f"  RECOMMENDED MANDI: {rec.mandi_name.upper()}")
    print("  " + "-"*63)
    print(f"  • Distance from {origin}: {rec.distance_km:.1f} km")
    print(f"  • Today's Modal Price:     ₹{rec.modal_price:,.0f} / quintal ({rec.benchmark_status})")
    print(f"  • Gross Produce Value:     ₹{rec.breakdown.gross_revenue:,.0f}")
    print(f"  • Road Freight:           -₹{rec.breakdown.freight_cost:,.0f} (Live Diesel @ ₹{rec.breakdown.diesel_price_per_litre:.2f}/L)")
    print(f"  • APMC Statutory Cess:    -₹{rec.breakdown.apmc_cess:,.0f} ({rec.breakdown.apmc_cess_percentage}%)")
    print(f"  • Hamali / Weighment:     -₹{rec.breakdown.weighment_loading:,.0f}")
    print(f"  • ICAR Spoilage Loss:     -₹{rec.breakdown.spoilage_loss_amount:,.0f} ({rec.breakdown.spoilage_percentage}% @ {rec.breakdown.transit_temperature:.1f}°C)")
    print(f"  • -------------------------------------------------------------")
    print(f"  • NET TAKE-HOME PROFIT:    ₹{rec.breakdown.net_profit:,.0f}")
    print(f"  • EXTRA GAIN OVER LOCAL:  +₹{rec.breakdown.profit_difference_vs_local:,.0f} 💰")
    print("  " + "-"*63)
    print(f"  🔮 Best Time to Sell: {result.best_time_to_sell}")
    print(f"  💡 Rationale: {result.prediction_rationale}")
    print(f"  🗣️ Indic Summary: {result.localized_explanation}\n")
    
    print("📊 ALTERNATIVE MANDIS EVALUATED:")
    for alt in result.alternative_mandis:
        print(f"  - {alt.mandi_name} ({alt.distance_km:.1f} km): Modal ₹{alt.modal_price:,.0f}/q | Net Take-Home: ₹{alt.breakdown.net_profit:,.0f} (Diff: ₹{alt.breakdown.profit_difference_vs_local:,.0f})")

    print("\n🏛️ MATCHED GOVERNMENT SCHEMES:")
    for s in result.eligible_schemes:
        print(f"  • [{s.scheme_name}] {s.title} -> {s.benefits} ({s.deep_link})")
    print("\n" + "="*65 + "\n")

def main():
    parser = argparse.ArgumentParser(description="KisanArbitrage Terminal CLI")
    parser.add_argument("--crop", default="Tomato", help="Commodity name (Tomato, Onion, Potato, Soybean, Cotton, Wheat)")
    parser.add_argument("--qty", type=float, default=20.0, help="Quantity")
    parser.add_argument("--unit", default="quintal", help="Unit (quintal, ton, kg)")
    parser.add_argument("--origin", default="Kolhapur", help="Origin City")
    parser.add_argument("--lat", type=float, default=16.6913, help="Origin Latitude")
    parser.add_argument("--lon", type=float, default=74.2432, help="Origin Longitude")
    parser.add_argument("--vehicle", default="bolero_pickup", help="Vehicle type (bolero_pickup, tata_ace, eicher_14ft)")
    
    args = parser.parse_args()
    asyncio.run(run_cli(args.crop, args.qty, args.unit, args.origin, args.lat, args.lon, args.vehicle))

if __name__ == "__main__":
    main()
