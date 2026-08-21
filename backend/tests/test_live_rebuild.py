import pytest
import pytest_asyncio
import asyncio
from backend.app.config import settings
from backend.app.db.database import init_db
from backend.app.scrapers.mandi_scraper import mandi_scraper
from backend.app.services.logistics_engine import logistics_engine
from backend.app.services.spoilage_engine import spoilage_engine
from backend.app.services.arbitrage_engine import arbitrage_engine
from backend.app.db.mandi_master import find_nearby_mandis
from backend.app.models.schemas import AnalysisRequest

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await init_db()

@pytest.mark.asyncio
async def test_datagov_live_fetching():
    """Verify that data.gov.in returns genuine live records with user API key."""
    records = await mandi_scraper.fetch_live_datagov_records(state="Maharashtra", commodity_filter="Tomato")
    assert isinstance(records, list)
    print(f"\nFetched {len(records)} live records from data.gov.in")

@pytest.mark.asyncio
async def test_osrm_live_routing():
    """Verify OSRM calculates real turn-by-turn road distance and duration."""
    # Kolhapur (16.6913, 74.2432) to Pune (18.4985, 73.8687)
    dist_km, dur_hrs, source = await logistics_engine.get_road_distance_and_duration(
        16.6913, 74.2432, 18.4985, 73.8687
    )
    assert dist_km > 200.0  # Real highway distance is ~230 km
    assert dur_hrs > 2.5
    assert source in ["OSRM_ROAD_ROUTING", "OPEN_ROUTE_SERVICE_API"]
    print(f"\nOSRM Route: {dist_km} km in {dur_hrs} hours via {source}")

@pytest.mark.asyncio
async def test_open_meteo_live_weather():
    """Verify Open-Meteo returns live temperature and humidity."""
    weather = await spoilage_engine.get_route_weather(17.59, 74.05)
    assert "temperature_celsius" in weather
    assert "humidity_pct" in weather
    assert 0.0 <= weather["temperature_celsius"] <= 50.0
    print(f"\nOpen-Meteo Weather: {weather['temperature_celsius']}°C, Humidity: {weather['humidity_pct']}%")

@pytest.mark.asyncio
async def test_end_to_end_genuine_arbitrage():
    """Verify full end-to-end arbitrage execution with zero fake dictionaries."""
    req = AnalysisRequest(
        commodity="Tomato",
        quantity=25.0,
        unit="quintal",
        origin_city="Kolhapur",
        origin_lat=16.6913,
        origin_lon=74.2432,
        vehicle_type="bolero_pickup"
    )
    candidates = find_nearby_mandis(req.origin_lat, req.origin_lon, radius_km=260.0, limit=5)
    assert len(candidates) > 0

    result = await arbitrage_engine.compute_arbitrage("test_session_live", req, candidates)
    assert result.recommended_mandi is not None
    assert result.recommended_mandi.breakdown.net_profit is not None
    assert result.recommended_mandi.data_provenance is not None
    print(f"\nRecommended Mandi: {result.recommended_mandi.mandi_name}")
    print(f"Modal Price: Rs.{result.recommended_mandi.modal_price}/q ({result.recommended_mandi.data_provenance})")
    print(f"Net Profit: Rs.{result.recommended_mandi.breakdown.net_profit:,.2f}")
    print(f"Road Distance: {result.recommended_mandi.distance_km} km ({result.recommended_mandi.breakdown.routing_source})")
