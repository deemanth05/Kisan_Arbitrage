import re
import json
import shutil
import asyncio
import logging
from datetime import datetime, UTC
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
from backend.app.config import settings
from backend.app.scrapers.bright_data_client import bright_data_client

logger = logging.getLogger(__name__)

# Official State-level Base Diesel Benchmarks for fallback disclosure (August 2026)
STATE_DIESEL_BENCHMARKS = {
    "maharashtra": 97.83,
    "karnataka": 88.80,
    "telangana": 103.82,
    "delhi": 95.20,
    "gujarat": 98.13,
    "default": 95.00
}

_diesel_cache: Dict[str, Dict[str, Any]] = {}

class FuelScraper:
    """
    Scrapes live district-level diesel rates using Bright Data Scraper Studio (Collector c_mt3e6r5yq1ojivj2h)
    and Web Unlocker to accurately index road freight transportation costs.
    """
    
    async def _fetch_from_scraper_studio(self) -> List[Dict[str, Any]]:
        """
        Executes the verified, healed Scraper Studio collector c_mt3e6r5yq1ojivj2h via bdata CLI.
        """
        collector_id = settings.COLLECTOR_DIESEL_PRICES
        if not collector_id:
            return []
            
        try:
            npx_cmd = shutil.which("npx") or "npx"
            target_url = "https://www.goodreturns.in/diesel-price-in-maharashtra.html"
            process = await asyncio.create_subprocess_exec(
                npx_cmd, "-p", "@brightdata/cli", "bdata", "scraper", "run",
                collector_id, target_url, "--pretty",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=35.0)
            if process.returncode == 0 and stdout:
                data = json.loads(stdout.decode("utf-8"))
                if isinstance(data, list):
                    return data
        except Exception as e:
            logger.warning(f"Scraper Studio collector query: {e}")
        return []

    async def get_diesel_price_info(self, city_or_district: str, state: str = "Maharashtra") -> Dict[str, Any]:
        city_clean = city_or_district.strip().lower()
        
        # Check in-memory cache (TTL: 6 hours)
        if city_clean in _diesel_cache:
            cache_entry = _diesel_cache[city_clean]
            if (datetime.now(UTC) - cache_entry["scraped_at"]).total_seconds() < 21600:
                return cache_entry

        # 1. Check Scraper Studio Collector data if state/city matches
        try:
            records = await self._fetch_from_scraper_studio()
            for r in records:
                name = (r.get("state_name") or "").strip().lower()
                price_obj = r.get("diesel_price")
                val = None
                if isinstance(price_obj, dict):
                    val = float(price_obj.get("value", 0))
                elif isinstance(price_obj, (int, float)):
                    val = float(price_obj)
                    
                if val and 80.0 <= val <= 115.0:
                    _diesel_cache[name] = {
                        "district": r.get("state_name", city_or_district),
                        "diesel_price": val,
                        "data_source": "BRIGHT_DATA_SCRAPER_STUDIO",
                        "scraped_at": datetime.now(UTC),
                        "is_live": True,
                        "provenance": f"Bright Data Scraper Studio ({settings.COLLECTOR_DIESEL_PRICES})"
                    }
                    
            if city_clean in _diesel_cache:
                return _diesel_cache[city_clean]
        except Exception as e:
            logger.warning(f"Error querying Scraper Studio fuel records: {e}")

        # 2. Scrape via Web Unlocker proxy
        url = f"https://www.goodreturns.in/diesel-price-in-{city_clean}.html"
        try:
            html = await bright_data_client.fetch_html(url, timeout=15.0, use_bright_data=True)
            if html:
                matches = re.findall(r"(?:Rs\.?|₹)\s*(\d{2}\.\d{2})", html)
                for m in matches:
                    p = float(m)
                    if 80.0 <= p <= 115.0:
                        res = {
                            "district": city_or_district,
                            "diesel_price": p,
                            "data_source": "BRIGHT_DATA_LIVE_SCRAPE",
                            "scraped_at": datetime.now(UTC),
                            "is_live": True,
                            "provenance": f"Live diesel rate scraped via Bright Data for {city_or_district}"
                        }
                        _diesel_cache[city_clean] = res
                        logger.info(f"Live diesel price scraped for {city_or_district}: ₹{p}/L")
                        return res
        except Exception as e:
            logger.warning(f"Bright Data fuel scraper for {city_or_district}: {e}")

        # 3. Transparent state-level fallback with clear provenance tag
        state_clean = state.strip().lower()
        fallback_rate = STATE_DIESEL_BENCHMARKS.get(state_clean, STATE_DIESEL_BENCHMARKS["default"])
        res = {
            "district": city_or_district,
            "diesel_price": fallback_rate,
            "data_source": "STATE_FUEL_BENCHMARK",
            "scraped_at": datetime.now(UTC),
            "is_live": False,
            "provenance": f"State-level diesel benchmark ({state.capitalize()})"
        }
        _diesel_cache[city_clean] = res
        return res

    async def get_diesel_price(self, city_or_district: str, state: str = "Maharashtra") -> float:
        info = await self.get_diesel_price_info(city_or_district, state)
        return float(info["diesel_price"])

fuel_scraper = FuelScraper()
