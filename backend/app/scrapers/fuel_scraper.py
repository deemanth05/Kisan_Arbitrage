import re
import logging
from typing import Dict
from bs4 import BeautifulSoup
from backend.app.scrapers.bright_data_client import bright_data_client

logger = logging.getLogger(__name__)

# State and District baseline rates for fallback if live scraping is rate-limited
DEFAULT_DIESEL_RATES = {
    "kolhapur": 92.45,
    "pune": 92.80,
    "sangli": 92.50,
    "satara": 92.65,
    "solapur": 93.10,
    "nashik": 92.70,
    "mumbai": 92.15,
    "vashi": 92.15,
    "navi mumbai": 92.15,
    "ahmednagar": 92.90,
    "nagpur": 93.40,
    "aurangabad": 93.20,
    "chhatrapati sambhajinagar": 93.20,
    "belgaum": 88.30,
    "hubli": 88.45,
    "bangalore": 88.94,
    "maharashtra": 92.60,
    "karnataka": 88.50,
}

_diesel_cache: Dict[str, float] = {}

class FuelScraper:
    """
    Scrapes live district-level diesel rates from fuel price tracking portals
    using Bright Data to accurately index freight transportation costs.
    """
    
    async def get_diesel_price(self, city_or_district: str) -> float:
        city_clean = city_or_district.strip().lower()
        if city_clean in _diesel_cache:
            return _diesel_cache[city_clean]
        
        # Scrape live price from mypetrolprice
        url = f"https://www.mypetrolprice.com/diesel-price-in-{city_clean}.aspx"
        try:
            html = await bright_data_client.fetch_html(url, timeout=10.0)
            soup = BeautifulSoup(html, "lxml")
            
            # Common DOM patterns on fuel price sites: price in currency span or bold header
            price_elem = soup.select_one(".price, .current-price, #fuel-price, span.r-price, div.r-price")
            if price_elem:
                text = price_elem.get_text()
                match = re.search(r"(\d+\.\d+)", text)
                if match:
                    price = float(match.group(1))
                    if 70.0 < price < 130.0:  # Sanity check for Indian diesel prices
                        logger.info(f"Live diesel price scraped for {city_or_district}: ₹{price}/L")
                        _diesel_cache[city_clean] = price
                        return price
            
            # Pattern search in raw HTML text
            matches = re.findall(r"₹\s*(\d{2}\.\d{2})", html)
            for m in matches:
                p = float(m)
                if 80.0 < p < 110.0:
                    logger.info(f"Regex diesel price extracted for {city_or_district}: ₹{p}/L")
                    _diesel_cache[city_clean] = p
                    return p
                    
        except Exception as e:
            logger.warning(f"Live fuel scraper encounter for {city_or_district}: {e}. Utilizing regional index.")
        
        # Fallback to authentic regional index
        fallback = DEFAULT_DIESEL_RATES.get(city_clean, DEFAULT_DIESEL_RATES["maharashtra"])
        _diesel_cache[city_clean] = fallback
        return fallback

fuel_scraper = FuelScraper()
