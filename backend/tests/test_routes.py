import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.db.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await init_db()

@pytest.mark.asyncio
async def test_health_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_system_status_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/system/status")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert "datagov_api" in data
        assert "osrm_routing" in data
        assert "open_meteo_weather" in data
        assert data["database"]["connected"] is True

@pytest.mark.asyncio
async def test_schemes_discover_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/schemes/discover?commodity=Tomato&state=Maharashtra")
        assert res.status_code == 200
        schemes = res.json()
        assert len(schemes) >= 3
        scheme_names = [s["scheme_name"] for s in schemes]
        assert "PM-KISAN" in scheme_names
        assert "PMFBY" in scheme_names

@pytest.mark.asyncio
async def test_mandis_nearby():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/mandis/nearby?lat=16.6913&lon=74.2432&radius=250")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] > 0
        assert any(m["district"] == "Pune" for m in data["mandis"])

@pytest.mark.asyncio
async def test_community_reports():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Fetch initial reports
        res = await ac.get("/api/v1/community/reports")
        assert res.status_code == 200
        assert len(res.json()) > 0
        
        # 2. Post new report
        new_report = {
            "mandi_id": "mandi_pune",
            "mandi_name": "Pune APMC",
            "commodity": "Tomato",
            "price_received": 2200.0,
            "quantity": 30.0,
            "farmer_name": "Dnyaneshwar Gaikwad",
            "farmer_location": "Saswad"
        }
        post_res = await ac.post("/api/v1/community/report", json=new_report)
        assert post_res.status_code == 200
        assert post_res.json()["price_received"] == 2200.0

@pytest.mark.asyncio
async def test_session_lifecycle_and_approval():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create session
        create_res = await ac.post("/api/v1/sessions", json={"device_id": "dev_test_123", "language": "hi"})
        assert create_res.status_code == 200
        sess_id = create_res.json()["session_id"]
        
        # Approve transport
        approve_res = await ac.post(
            f"/api/v1/sessions/{sess_id}/approve",
            json={"session_id": sess_id, "mandi_id": "mandi_pune"}
        )
        assert approve_res.status_code == 200
        assert approve_res.json()["status"] == "APPROVED"
