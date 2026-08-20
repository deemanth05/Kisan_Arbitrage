import math
import httpx
import logging
from typing import Dict, Any, Tuple
from backend.app.config import settings
from backend.app.scrapers.fuel_scraper import fuel_scraper

logger = logging.getLogger(__name__)

VEHICLE_PROFILES = {
    "tata_ace": {
        "name": "Tata Ace (Chota Hathi)",
        "capacity_quintals": 15.0,  # 1.5 tons
        "mileage_kmpl": 14.0,
        "base_hire": 500.0,
        "driver_bata": 300.0,
    },
    "bolero_pickup": {
        "name": "Mahindra Bolero Maxi Truck",
        "capacity_quintals": 25.0,  # 2.5 tons
        "mileage_kmpl": 11.0,
        "base_hire": 750.0,
        "driver_bata": 400.0,
    },
    "eicher_14ft": {
        "name": "Eicher 14ft Commercial Truck",
        "capacity_quintals": 50.0,  # 5.0 tons
        "mileage_kmpl": 7.0,
        "base_hire": 1400.0,
        "driver_bata": 600.0,
    }
}

class LogisticsEngine:
    """
    Computes freight and transport economics based on live district fuel prices,
    road distance from OpenRouteService, and Indian commercial vehicle specifications.
    """
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates straight line distance in km."""
        r = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (
            math.sin(d_lat / 2.0) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(d_lon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    async def get_route_matrix(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float
    ) -> Tuple[float, float]:
        """
        Gets driving distance (km) and driving duration (hours) from OpenRouteService.
        Falls back to haversine with Indian road curvature coefficient (1.28x) if needed.
        """
        if settings.OPEN_ROUTE_API_KEY:
            url = "https://api.openrouteservice.org/v2/directions/driving-car"
            headers = {"Authorization": settings.OPEN_ROUTE_API_KEY}
            params = {
                "start": f"{origin_lon},{origin_lat}",
                "end": f"{dest_lon},{dest_lat}"
            }
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.get(url, headers=headers, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        summary = data["features"][0]["properties"]["summary"]
                        dist_km = summary["distance"] / 1000.0
                        duration_hrs = summary["duration"] / 3600.0
                        return round(dist_km, 1), round(duration_hrs, 2)
            except Exception as e:
                logger.warning(f"OpenRouteService routing error: {e}. Falling back to road curvature model.")
                
        # High-accuracy road curvature model for Indian state highways
        crow_dist = self.haversine_distance(origin_lat, origin_lon, dest_lat, dest_lon)
        if crow_dist < 5.0:
            return round(crow_dist, 1), 0.15  # Local mandi
            
        road_distance = crow_dist * 1.28  # 1.28x highway tortuosity factor in Western Ghats & Deccan
        avg_speed_kmh = 45.0  # Average laden truck speed on Indian state/national highways
        duration_hrs = road_distance / avg_speed_kmh
        return round(road_distance, 1), round(duration_hrs, 2)

    async def calculate_freight(
        self,
        origin_city: str,
        distance_km: float,
        vehicle_type: str = "bolero_pickup"
    ) -> Tuple[float, float, float]:
        """
        Calculates total freight cost factoring in live diesel rates, return trip, and tolls.
        Returns: (total_freight_cost, live_diesel_price, toll_estimate)
        """
        if distance_km <= 5.0:
            # Local mandi transport (tractor/auto loading)
            return 350.0, 92.40, 0.0
            
        vehicle = VEHICLE_PROFILES.get(vehicle_type, VEHICLE_PROFILES["bolero_pickup"])
        live_diesel = await fuel_scraper.get_diesel_price(origin_city)
        
        # Round trip fuel requirement (return empty trip factor = 1.85x fuel)
        total_fuel_litres = (distance_km * 1.85) / vehicle["mileage_kmpl"]
        fuel_cost = total_fuel_litres * live_diesel
        
        # NHAI / State Toll estimation (~₹0.80 per km on routes > 50 km)
        tolls = (distance_km * 0.80) if distance_km > 50.0 else 0.0
        
        total_freight = vehicle["base_hire"] + fuel_cost + vehicle["driver_bata"] + tolls
        return round(total_freight, 2), round(live_diesel, 2), round(tolls, 2)

logistics_engine = LogisticsEngine()
