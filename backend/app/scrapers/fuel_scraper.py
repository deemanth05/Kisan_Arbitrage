import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from backend.app.config import settings
from backend.app.scrapers.bright_data_client import bright_data_client

logger = logging.getLogger(__name__)

# Official State-level Base Diesel Benchmarks for fallback disclosure (August 2026)
STATE_DIESEL_BENCHMARKS = {
    "maharashtra": 98.50,
    "karnataka": 88.50,
    "default": 94.00
}

_diesel_cache: Dict[str, Dict[str, Any]] = {}

class FuelScraper:
    """
    Scrapes live district-level diesel rates from fuel price tracking portals
    using Bright Data Web Unlocker proxy to accurately index freight transportation costs.
    """
    
    async def get_diesel_price_info(self, city_or_district: str, state: str = "Maharashtra") -> Dict[str, Any]:
        city_clean = city_or_district.strip().lower()
        
        # Check in-memory cache (TTL: 6 hours)
        if city_clean in _diesel_cache:
            cache_entry = _diesel_cache[city_clean]
            if (datetime.utcnow() - cache_entry["scraped_at"]).total_seconds() < 21600:
                return cache_entry

        # 1. Attempt scraping live price from NDTV / Goodreturns via Bright Data
        url = f"https://www.ndtv.com/fuel-prices/diesel-price-in-{city_clean}-district"
        try:
            html = await bright_data_client.fetch_html(url, timeout=12.0, use_bright_data=True)
            if html:
                matches = re.findall(r"(?:Rs\.?|₹)\s*(\d{2}\.\d{2})", html)
                for m in matches:
                    p = float(m)
                    if 80.0 <= p <= 110.0:
                        res = {
                            "district": city_or_district,
                            "diesel_price": p,
                            "data_source": "BRIGHT_DATA_LIVE_SCRAPE",
                            "scraped_at": datetime.utcnow(),
                            "is_live": True,
                            "provenance": f"Live fuel index scraped via Bright Data for {city_or_district}"
                        }
                        _diesel_cache[city_clean] = res
                        logger.info(f"Live diesel price scraped for {city_or_district}: ₹{p}/L")
                        return res
        except Exception as e:
            logger.warning(f"Bright Data fuel scraper for {city_or_district}: {e}")

        # 2. Transparent state-level fallback with clear provenance tag
        state_clean = state.strip().lower()
        fallback_rate = STATE_DIESEL_BENCHMARKS.get(state_clean, STATE_DIESEL_BENCHMARKS["default"])
        res = {
            "district": city_or_district,
            "diesel_price": fallback_rate,
            "data_source": "STATE_FUEL_BENCHMARK",
            "scraped_at": datetime.utcnow(),
            "is_live": False,
            "provenance": f"State-level diesel benchmark ({state.capitalize()})"
        }
        _diesel_cache[city_clean] = res
        return res

    async def get_diesel_price(self, city_or_district: str, state: str = "Maharashtra") -> float:
        info = await self.get_diesel_price_info(city_or_district, state)
        return float(info["diesel_price"])

fuel_scraper = FuelScraper()
