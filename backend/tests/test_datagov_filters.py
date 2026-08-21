import asyncio
import httpx

async def test_filters():
    api_key = "579b464db66ec23bdd00000161f10f9e2001428979c3359cf2570ccc"
    url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={api_key}&format=json&offset=0&limit=5&filters[state]=Maharashtra"
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url)
        assert resp.status_code == 200

if __name__ == "__main__":
    asyncio.run(test_filters())
