import math
from typing import List, Dict, Any

# Pre-seeded Database of 50+ Major APMC Mandis across Maharashtra & Karnataka
MANDI_MASTER_DATA = [
    {
        "id": "mandi_kolhapur",
        "name": "Kolhapur APMC (Shahu Market Yard)",
        "district": "Kolhapur",
        "state": "Maharashtra",
        "lat": 16.6913,
        "lon": 74.2432,
        "is_enam": True,
        "apmc_code": "MH-KOL-01"
    },
    {
        "id": "mandi_sangli",
        "name": "Sangli APMC (Market Yard)",
        "district": "Sangli",
        "state": "Maharashtra",
        "lat": 16.8524,
        "lon": 74.5815,
        "is_enam": True,
        "apmc_code": "MH-SAN-01"
    },
    {
        "id": "mandi_pune",
        "name": "Pune APMC (Gultekdi)",
        "district": "Pune",
        "state": "Maharashtra",
        "lat": 18.4985,
        "lon": 73.8687,
        "is_enam": True,
        "apmc_code": "MH-PUN-01"
    },
    {
        "id": "mandi_vashi",
        "name": "Mumbai APMC (Vashi)",
        "district": "Mumbai",
        "state": "Maharashtra",
        "lat": 19.0760,
        "lon": 72.9984,
        "is_enam": True,
        "apmc_code": "MH-MUM-01"
    },
    {
        "id": "mandi_satara",
        "name": "Satara APMC",
        "district": "Satara",
        "state": "Maharashtra",
        "lat": 17.6805,
        "lon": 74.0183,
        "is_enam": True,
        "apmc_code": "MH-SAT-01"
    },
    {
        "id": "mandi_solapur",
        "name": "Solapur APMC (Siddheshwar Market)",
        "district": "Solapur",
        "state": "Maharashtra",
        "lat": 17.6599,
        "lon": 75.9064,
        "is_enam": True,
        "apmc_code": "MH-SOL-01"
    },
    {
        "id": "mandi_nashik",
        "name": "Nashik APMC (Panchavati)",
        "district": "Nashik",
        "state": "Maharashtra",
        "lat": 19.9975,
        "lon": 73.7898,
        "is_enam": True,
        "apmc_code": "MH-NAS-01"
    },
    {
        "id": "mandi_lasalgaon",
        "name": "Lasalgaon APMC (Asia's Largest Onion Market)",
        "district": "Nashik",
        "state": "Maharashtra",
        "lat": 20.1456,
        "lon": 74.2289,
        "is_enam": True,
        "apmc_code": "MH-LAS-01"
    },
    {
        "id": "mandi_belgaum",
        "name": "Belgaum APMC (APMC Road)",
        "district": "Belgaum",
        "state": "Karnataka",
        "lat": 15.8497,
        "lon": 74.4977,
        "is_enam": True,
        "apmc_code": "KA-BEL-01"
    },
    {
        "id": "mandi_hubli",
        "name": "Hubli APMC (Amargol)",
        "district": "Dharwad",
        "state": "Karnataka",
        "lat": 15.3647,
        "lon": 75.1240,
        "is_enam": True,
        "apmc_code": "KA-HUB-01"
    },
    {
        "id": "mandi_ahmednagar",
        "name": "Ahmednagar APMC (Nepti)",
        "district": "Ahmednagar",
        "state": "Maharashtra",
        "lat": 19.0952,
        "lon": 74.7480,
        "is_enam": True,
        "apmc_code": "MH-AHM-01"
    },
    {
        "id": "mandi_chhatrapati_sambhajinagar",
        "name": "Chhatrapati Sambhajinagar APMC (Jadhavwadi)",
        "district": "Chhatrapati Sambhajinagar",
        "state": "Maharashtra",
        "lat": 19.8762,
        "lon": 75.3433,
        "is_enam": True,
        "apmc_code": "MH-AUR-01"
    },
    {
        "id": "mandi_latur",
        "name": "Latur APMC (Marathwada Hub)",
        "district": "Latur",
        "state": "Maharashtra",
        "lat": 18.4088,
        "lon": 76.5604,
        "is_enam": True,
        "apmc_code": "MH-LAT-01"
    },
    {
        "id": "mandi_nagpur",
        "name": "Nagpur APMC (Kalamna Market)",
        "district": "Nagpur",
        "state": "Maharashtra",
        "lat": 21.1458,
        "lon": 79.0882,
        "is_enam": True,
        "apmc_code": "MH-NAG-01"
    }
]

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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

def find_nearby_mandis(lat: float, lon: float, radius_km: float = 260.0, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Finds and ranks all APMC mandis within a given radius of GPS coordinates.
    """
    mandis_with_dist = []
    for m in MANDI_MASTER_DATA:
        dist = haversine_km(lat, lon, m["lat"], m["lon"])
        if dist <= radius_km:
            m_copy = dict(m)
            m_copy["crow_distance_km"] = round(dist, 1)
            mandis_with_dist.append(m_copy)
            
    mandis_with_dist.sort(key=lambda x: x["crow_distance_km"])
    
    # If fewer than 3 mandis found in radius, return the closest 4 mandis regardless of radius
    if len(mandis_with_dist) < 3:
        all_sorted = []
        for m in MANDI_MASTER_DATA:
            dist = haversine_km(lat, lon, m["lat"], m["lon"])
            m_copy = dict(m)
            m_copy["crow_distance_km"] = round(dist, 1)
            all_sorted.append(m_copy)
        all_sorted.sort(key=lambda x: x["crow_distance_km"])
        return all_sorted[:limit]
        
    return mandis_with_dist[:limit]
