import math
import logging
from typing import Dict, Tuple, Optional, Any
import httpx

logger = logging.getLogger(__name__)

# ICAR-CIPHET Physical Crop Perishability Parameters
CROP_PERISHABILITY_PROFILES: Dict[str, Dict[str, Any]] = {
    "tomato": {
        "is_perishable": True,
        "base_safe_temp": 20.0,
        "base_loss_pct_per_hour": 0.25,
        "heat_decay_factor": 0.08,    # accelerated rot above 25°C
        "rain_decay_factor": 0.35,    # moisture mold acceleration
        "max_loss_cap": 0.25          # max 25% value loss
    },
    "onion": {
        "is_perishable": False,       # semi-perishable
        "base_safe_temp": 28.0,
        "base_loss_pct_per_hour": 0.04,
        "heat_decay_factor": 0.015,
        "rain_decay_factor": 0.20,    # rain causes rapid black mold on onion
        "max_loss_cap": 0.12
    },
    "potato": {
        "is_perishable": False,
        "base_safe_temp": 25.0,
        "base_loss_pct_per_hour": 0.03,
        "heat_decay_factor": 0.01,
        "rain_decay_factor": 0.15,
        "max_loss_cap": 0.10
    },
    "soybean": {
        "is_perishable": False,       # dry grain/oilseed
        "base_safe_temp": 38.0,
        "base_loss_pct_per_hour": 0.0,
        "heat_decay_factor": 0.0,
        "rain_decay_factor": 0.05,    # only rain causes bag moisture damage
        "max_loss_cap": 0.05
    },
    "cotton": {
        "is_perishable": False,
        "base_safe_temp": 40.0,
        "base_loss_pct_per_hour": 0.0,
        "heat_decay_factor": 0.0,
        "rain_decay_factor": 0.10,    # waterlogging stains cotton fiber
        "max_loss_cap": 0.08
    },
    "wheat": {
        "is_perishable": False,
        "base_safe_temp": 40.0,
        "base_loss_pct_per_hour": 0.0,
        "heat_decay_factor": 0.0,
        "rain_decay_factor": 0.05,
        "max_loss_cap": 0.05
    }
}

class SpoilageEngine:
    """
    Computes scientific ICAR-CIPHET post-harvest spoilage and transit degradation
    indexed against real-time Open-Meteo route temperature and precipitation forecasts.
    """

    async def get_route_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetches live ambient temperature, humidity, and rain status from Open-Meteo.
        """
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat:.4f}&longitude={lon:.4f}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code&timezone=Asia/Kolkata"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    current = data.get("current", {})
                    temp = float(current.get("temperature_2m", 28.0))
                    precip = float(current.get("precipitation", 0.0))
                    humidity = float(current.get("relative_humidity_2m", 60.0))
                    return {
                        "temperature_celsius": temp,
                        "precipitation_mm": precip,
                        "humidity_pct": humidity,
                        "has_rain": precip > 0.1,
                        "data_source": "OPEN_METEO_LIVE"
                    }
        except Exception as e:
            logger.warning(f"Open-Meteo API query error: {e}")

        # Fallback to authentic seasonal average for Deccan plateau
        return {
            "temperature_celsius": 28.5,
            "precipitation_mm": 0.0,
            "humidity_pct": 65.0,
            "has_rain": False,
            "data_source": "SEASONAL_REGIONAL_AVERAGE"
        }

    def calculate_spoilage(
        self,
        commodity: str,
        gross_value: float,
        transit_duration_hours: float,
        ambient_temperature: float,
        has_rain: bool
    ) -> Tuple[float, float]:
        """
        Calculates (spoilage_loss_rupees, spoilage_percentage) based on ICAR-CIPHET physiological decay.
        """
        comm_clean = commodity.strip().lower()
        profile = CROP_PERISHABILITY_PROFILES.get(comm_clean, CROP_PERISHABILITY_PROFILES["tomato"])
        
        # Non-perishable dry crops with no rain have zero transit loss
        if not profile["is_perishable"] and not has_rain:
            return 0.0, 0.0

        # Base time decay
        loss_pct = profile["base_loss_pct_per_hour"] * transit_duration_hours

        # Thermal excess factor
        excess_heat = max(0.0, ambient_temperature - profile["base_safe_temp"])
        heat_decay = excess_heat * profile["heat_decay_factor"] * transit_duration_hours
        loss_pct += heat_decay

        # Moisture factor
        if has_rain:
            loss_pct += profile["rain_decay_factor"] * transit_duration_hours

        # Cap loss percentage by physical profile limits
        final_pct = min(loss_pct, profile["max_loss_cap"] * 100.0)
        spoilage_rupees = gross_value * (final_pct / 100.0)

        return round(spoilage_rupees, 2), round(final_pct, 2)

spoilage_engine = SpoilageEngine()
