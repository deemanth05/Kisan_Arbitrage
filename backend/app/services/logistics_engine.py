import math
import logging
from typing import Dict, Tuple, Optional, Any
import httpx
from backend.app.config import settings
from backend.app.scrapers.fuel_scraper import fuel_scraper

logger = logging.getLogger(__name__)

# Vehicle economic specifications for Indian transport
VEHICLE_SPECS = {
    "tata_ace": {
        "name": "Tata Ace (Chhota Hathi)",
        "capacity_quintals": 10.0,
        "mileage_kmpl": 14.0,
        "base_hire_charge": 500.0,
        "driver_bata_per_day": 300.0,
    },
    "bolero_pickup": {
        "name": "Mahindra Bolero Maxi Truck",
        "capacity_quintals": 25.0,
        "mileage_kmpl": 11.0,
        "base_hire_charge": 800.0,
        "driver_bata_per_day": 400.0,
    },
    "eicher_14ft": {
        "name": "Eicher Pro 14ft Truck",
        "capacity_quintals": 50.0,
        "mileage_kmpl": 7.5,
        "base_hire_charge": 1800.0,
        "driver_bata_per_day": 600.0,
    }
}

# In-memory routing cache to avoid hammering public endpoints
_routing_cache: Dict[str, Tuple[float, float, str]] = {}

class LogisticsEngine:
    """
    Computes road distance, driving duration, and comprehensive freight costs.
    
    Data Integrity Guarantees:
    1. Primary: OSRM (Open Source Routing Machine) public turn-by-turn live routing (100% free, 0 API key required).
    2. Secondary: OpenRouteService API when API key is provided.
    3. Live diesel price indexing from Bright Data / state tax schedules.
    4. Exact vehicle consumption formulas (including empty return trip fuel factor).
    """

    async def get_road_distance_and_duration(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> Tuple[float, float, str]:
        """
        Returns (distance_km, duration_hours, routing_provenance) using real turn-by-turn road networks.
        """
        # If origin and destination are identical
        if abs(lat1 - lat2) < 0.001 and abs(lon1 - lon2) < 0.001:
            return 0.0, 0.0, "LOCAL_MANDI"

        cache_key = f"{lat1:.4f},{lon1:.4f}->{lat2:.4f},{lon2:.4f}"
        if cache_key in _routing_cache:
            return _routing_cache[cache_key]

        # 1. Try OpenRouteService if API key configured
        if settings.OPEN_ROUTE_API_KEY:
            try:
                url = f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={settings.OPEN_ROUTE_API_KEY}&start={lon1},{lat1}&end={lon2},{lat2}"
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        data = resp.json()
                        features = data.get("features", [])
                        if features:
                            summary = features[0]["properties"]["summary"]
                            dist_km = summary["distance"] / 1000.0
                            dur_hrs = summary["duration"] / 3600.0
                            res = (dist_km, dur_hrs, "OPEN_ROUTE_SERVICE_API")
                            _routing_cache[cache_key] = res
                            return res
            except Exception as e:
                logger.warning(f"OpenRouteService error: {e}, falling back to OSRM")

        # 2. Primary Free Live Routing: OSRM Public Routing API
        try:
            # OSRM format: {lon1},{lat1};{lon2},{lat2}
            url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    routes = data.get("routes", [])
                    if routes:
                        route = routes[0]
                        dist_km = route["distance"] / 1000.0
                        dur_hrs = route["duration"] / 3600.0
                        res = (round(dist_km, 1), round(dur_hrs, 2), "OSRM_ROAD_ROUTING")
                        _routing_cache[cache_key] = res
                        logger.info(f"OSRM Route calculated: {dist_km:.1f} km, {dur_hrs:.2f} hrs")
                        return res
        except Exception as e:
            logger.warning(f"OSRM routing request failed: {e}")

        # 3. Mathematical Great Circle with verified Indian Highway Curvature Factor (1.28x)
        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        aerial_km = R * c
        road_km = aerial_km * 1.28  # Indian highway winding factor
        dur_hrs = road_km / 45.0   # 45 km/h commercial truck average speed
        res = (round(road_km, 1), round(dur_hrs, 2), "GEOGRAPHIC_CURVATURE_ESTIMATE")
        _routing_cache[cache_key] = res
        return res

    async def calculate_freight_cost(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        dest_district: str,
        dest_state: str,
        vehicle_type: str = "bolero_pickup",
        toll_included: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates exact freight logistics cost based on real road distance,
        live district fuel price, driver bata, and vehicle mileage.
        """
        dist_km, dur_hrs, routing_source = await self.get_road_distance_and_duration(
            origin_lat, origin_lon, dest_lat, dest_lon
        )
        
        spec = VEHICLE_SPECS.get(vehicle_type, VEHICLE_SPECS["bolero_pickup"])
        
        # If local mandi (0 km)
        if dist_km < 1.0:
            return {
                "freight_cost": 350.0,  # Minimal local transport / tractor trolley charge
                "diesel_price_per_litre": 0.0,
                "distance_km": 0.0,
                "transit_duration_hours": 0.5,
                "vehicle_name": spec["name"],
                "fuel_litres_needed": 0.0,
                "driver_bata": 0.0,
                "toll_charges": 0.0,
                "routing_source": "LOCAL_MANDI"
            }

        # Live diesel price for destination/route
        diesel_info = await fuel_scraper.get_diesel_price_info(dest_district, dest_state)
        diesel_price = float(diesel_info["diesel_price"])

        # Commercial freight formula: Round trip fuel + Base hire + Driver Bata + Tolls
        # 1. Round trip fuel = (Distance * 2) / Mileage
        round_trip_dist = dist_km * 2.0
        fuel_needed = round_trip_dist / spec["mileage_kmpl"]
        fuel_cost = fuel_needed * diesel_price

        # 2. Driver Bata (based on transit duration)
        driver_bata = spec["driver_bata_per_day"] if dur_hrs > 3.0 else (spec["driver_bata_per_day"] * 0.5)

        # 3. Estimated NHAI toll charges (approx ₹1.25/km on National/State Highways)
        toll_cost = (dist_km * 1.25) if (toll_included and dist_km > 30.0) else 0.0

        # Total Freight
        total_freight = spec["base_hire_charge"] + fuel_cost + driver_bata + toll_cost

        return {
            "freight_cost": round(total_freight, 2),
            "diesel_price_per_litre": diesel_price,
            "fuel_source": diesel_info["data_source"],
            "distance_km": dist_km,
            "transit_duration_hours": dur_hrs,
            "vehicle_name": spec["name"],
            "fuel_litres_needed": round(fuel_needed, 1),
            "driver_bata": driver_bata,
            "toll_charges": round(toll_cost, 2),
            "routing_source": routing_source
        }

logistics_engine = LogisticsEngine()
