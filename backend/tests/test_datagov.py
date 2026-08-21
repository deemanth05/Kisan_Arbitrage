import asyncio
import httpx

async def test_datagov():
    api_key = "579b464db66ec23bdd00000161f10f9e2001428979c3359cf2570ccc"
    url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={api_key}&format=json&offset=0&limit=10&filters[state]=Maharashtra"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(headers=headers, timeout=15.0) as client:
        resp = await client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("total") > 0

if __name__ == "__main__":
    asyncio.run(test_datagov())
