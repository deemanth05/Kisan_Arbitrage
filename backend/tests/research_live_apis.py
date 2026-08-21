import asyncio
import httpx

async def test_all():
    url = "http://router.project-osrm.org/route/v1/driving/74.2432,16.6913;73.8687,18.4985?overview=false"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        assert resp.status_code == 200

if __name__ == "__main__":
    asyncio.run(test_all())
