import httpx
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# ICAR-CIPHET Perishability Coefficients
# Respiration and thermal decay rates per commodity class
CROP_PERISHABILITY_PROFILES = {
    "tomato": {
        "class": "HIGH_PERISHABLE",
        "safe_temp_celsius": 24.0,
        "base_loss_pct": 1.5,
        "temp_decay_rate_per_hr": 0.08,  # % loss per hour per degree C above safe temp
        "rain_decay_rate_per_hr": 0.5,
        "max_spoilage_cap_pct": 25.0,
    },
    "green_chilli": {
        "class": "HIGH_PERISHABLE",
        "safe_temp_celsius": 26.0,
        "base_loss_pct": 1.2,
        "temp_decay_rate_per_hr": 0.06,
        "rain_decay_rate_per_hr": 0.4,
        "max_spoilage_cap_pct": 20.0,
    },
    "onion": {
        "class": "SEMI_PERISHABLE",
        "safe_temp_celsius": 36.0,
        "base_loss_pct": 0.3,
        "temp_decay_rate_per_hr": 0.015,
        "rain_decay_rate_per_hr": 0.25,
        "max_spoilage_cap_pct": 10.0,
    },
    "potato": {
        "class": "SEMI_PERISHABLE",
        "safe_temp_celsius": 32.0,
        "base_loss_pct": 0.4,
        "temp_decay_rate_per_hr": 0.02,
        "rain_decay_rate_per_hr": 0.3,
        "max_spoilage_cap_pct": 12.0,
    },
    "soybean": {
        "class": "NON_PERISHABLE",
        "safe_temp_celsius": 45.0,
        "base_loss_pct": 0.0,
        "temp_decay_rate_per_hr": 0.0,
        "rain_decay_rate_per_hr": 0.1,  # Rain can cause moisture damage
        "max_spoilage_cap_pct": 5.0,
    },
    "cotton": {
        "class": "NON_PERISHABLE",
        "safe_temp_celsius": 45.0,
        "base_loss_pct": 0.0,
        "temp_decay_rate_per_hr": 0.0,
        "rain_decay_rate_per_hr": 0.15,
        "max_spoilage_cap_pct": 5.0,
    },
    "wheat": {
        "class": "NON_PERISHABLE",
        "safe_temp_celsius": 45.0,
        "base_loss_pct": 0.0,
        "temp_decay_rate_per_hr": 0.0,
        "rain_decay_rate_per_hr": 0.1,
        "max_spoilage_cap_pct": 5.0,
    },
    "maize": {
        "class": "NON_PERISHABLE",
        "safe_temp_celsius": 45.0,
        "base_loss_pct": 0.0,
        "temp_decay_rate_per_hr": 0.0,
        "rain_decay_rate_per_hr": 0.1,
        "max_spoilage_cap_pct": 5.0,
    }
}

class SpoilageEngine:
    """
    Calculates post-harvest transit spoilage risk using ICAR-CIPHET equations
    and real-time route weather data from Open-Meteo.
    """
    
    async def fetch_route_weather(self, lat: float, lon: float) -> Tuple[float, bool]:
        """
        Queries Open-Meteo for real-time ambient temperature and precipitation.
        No API key required.
        """
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
            "timezone": "Asia/Kolkata"
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                current = data.get("current", {})
                temp = current.get("temperature_2m", 32.0)
                precip = current.get("precipitation", 0.0)
                has_rain = precip > 0.1 or current.get("weather_code", 0) in [51, 53, 55, 61, 63, 65, 80, 81, 82]
                logger.info(f"Open-Meteo route weather at ({lat}, {lon}): {temp}°C, Rain: {has_rain}")
                return float(temp), bool(has_rain)
        except Exception as e:
            logger.warning(f"Open-Meteo weather fetch error for ({lat}, {lon}): {e}. Using seasonal baseline.")
            return 33.5, False

    def calculate_spoilage(
        self,
        commodity: str,
        gross_value: float,
        transit_hours: float,
        temperature: float,
        has_rain: bool
    ) -> Tuple[float, float]:
        """
        Calculates the spoilage percentage and monetary value loss.
        Returns: (spoilage_loss_rupees, spoilage_percentage)
        """
        crop_clean = commodity.strip().lower().replace(" ", "_")
        profile = CROP_PERISHABILITY_PROFILES.get(crop_clean, CROP_PERISHABILITY_PROFILES["tomato"])
        
        # If transport is under 15 mins (local mandi sale), zero transit decay
        if transit_hours <= 0.25:
            return 0.0, 0.0
            
        base_loss = profile["base_loss_pct"]
        excess_temp = max(0.0, temperature - profile["safe_temp_celsius"])
        temp_loss = excess_temp * profile["temp_decay_rate_per_hr"] * transit_hours
        
        rain_loss = (profile["rain_decay_rate_per_hr"] * transit_hours) if has_rain else 0.0
        
        total_spoilage_pct = min(base_loss + temp_loss + rain_loss, profile["max_spoilage_cap_pct"])
        total_loss_rupees = gross_value * (total_spoilage_pct / 100.0)
        
        return round(total_loss_rupees, 2), round(total_spoilage_pct, 2)

spoilage_engine = SpoilageEngine()
