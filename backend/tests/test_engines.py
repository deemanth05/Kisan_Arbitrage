import pytest
import pytest_asyncio
from backend.app.services.spoilage_engine import spoilage_engine
from backend.app.services.logistics_engine import logistics_engine
from backend.app.services.msp_engine import msp_engine
from backend.app.services.scheme_engine import scheme_engine
from backend.app.services.arbitrage_engine import arbitrage_engine
from backend.app.models.schemas import AnalysisRequest

@pytest.mark.asyncio
async def test_spoilage_calculation():
    # 1. High heat tomato transit (4 hours @ 38°C)
    loss_amt, loss_pct = spoilage_engine.calculate_spoilage(
        commodity="tomato",
        gross_value=40000.0,
        transit_hours=4.0,
        temperature=38.0,
        has_rain=False
    )
    assert loss_pct > 2.0
    assert loss_amt > 800.0
    
    # 2. Local sale (transit under 15 mins) -> 0 loss
    local_loss, local_pct = spoilage_engine.calculate_spoilage(
        commodity="tomato",
        gross_value=40000.0,
        transit_hours=0.1,
        temperature=38.0,
        has_rain=False
    )
    assert local_loss == 0.0
    assert local_pct == 0.0
    
    # 3. Non-perishable soybean
    soy_loss, soy_pct = spoilage_engine.calculate_spoilage(
        commodity="soybean",
        gross_value=80000.0,
        transit_hours=5.0,
        temperature=40.0,
        has_rain=False
    )
    assert soy_pct == 0.0
    assert soy_loss == 0.0

@pytest.mark.asyncio
async def test_logistics_freight_model():
    freight, diesel, tolls = await logistics_engine.calculate_freight(
        origin_city="Kolhapur",
        distance_km=230.0,  # Kolhapur to Pune
        vehicle_type="bolero_pickup"
    )
    assert freight > 2000.0
    assert diesel > 80.0
    assert tolls > 0.0

def test_msp_and_top_benchmarks():
    # 1. Soybean (Statutory MSP)
    soy_bench = msp_engine.evaluate_benchmark("soybean", 4650.0)
    assert "MSP" in soy_bench["benchmark_name"]
    assert soy_bench["benchmark_price"] == 4892.0
    assert soy_bench["benchmark_status"] == "BELOW_BENCHMARK"
    
    # 2. Tomato (TOP Operation Greens Benchmark)
    tom_bench = msp_engine.evaluate_benchmark("tomato", 2150.0)
    assert "TOP" in tom_bench["benchmark_name"]
    assert tom_bench["benchmark_price"] == 1750.0
    assert tom_bench["benchmark_status"] == "ABOVE_BENCHMARK"

def test_scheme_eligibility():
    schemes = scheme_engine.get_eligible_schemes("tomato")
    scheme_codes = [s.scheme_code for s in schemes]
    assert "PM_KISAN" in scheme_codes
    assert "PMFBY" in scheme_codes
    assert "OPERATION_GREENS" in scheme_codes

@pytest.mark.asyncio
async def test_arbitrage_ranking():
    req = AnalysisRequest(
        commodity="Tomato",
        quantity=20.0,
        unit="quintal",
        origin_city="Kolhapur",
        origin_lat=16.6913,
        origin_lon=74.2432,
        vehicle_type="bolero_pickup"
    )
    candidate_mandis = [
        {"id": "mandi_kolhapur", "name": "Kolhapur APMC", "district": "Kolhapur", "state": "Maharashtra", "lat": 16.6913, "lon": 74.2432},
        {"id": "mandi_sangli", "name": "Sangli APMC", "district": "Sangli", "state": "Maharashtra", "lat": 16.8524, "lon": 74.5815},
        {"id": "mandi_pune", "name": "Pune APMC", "district": "Pune", "state": "Maharashtra", "lat": 18.4985, "lon": 73.8687}
    ]
    result = await arbitrage_engine.compute_arbitrage("test_session", req, candidate_mandis)
    assert result.recommended_mandi is not None
    assert result.recommended_mandi.breakdown.net_profit > 0
    assert len(result.alternative_mandis) >= 2
    assert result.best_time_to_sell in ["SELL_TODAY", "WAIT_2_3_DAYS"]
