import asyncio
from backend.app.scrapers.bright_data_client import bright_data_client

async def test_bdata_scrape():
    url = "https://www.goodreturns.in/diesel-price.html"
    print(f"Testing Bright Data CLI scrape on {url}...")
    html = await bright_data_client.fetch_html(url, use_bright_data=True)
    print(f"Successfully scraped {len(html)} bytes via Bright Data!")
    assert len(html) > 100

if __name__ == "__main__":
    asyncio.run(test_bdata_scrape())
