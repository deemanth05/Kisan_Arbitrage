from fastapi import APIRouter, Query
from typing import List, Dict, Any
from backend.app.db.mandi_master import find_nearby_mandis, MANDI_MASTER_DATA

router = APIRouter(prefix="/api/v1/mandis", tags=["Mandis & Discovery"])

@router.get("/nearby")
async def get_nearby_mandis(
    lat: float = Query(16.6913, description="Latitude of farmer location (default: Kolhapur)"),
    lon: float = Query(74.2432, description="Longitude of farmer location"),
    radius: float = Query(260.0, description="Search radius in kilometers"),
    limit: int = Query(6, description="Max mandis to return")
) -> Dict[str, Any]:
    """
    Returns candidate APMC mandis within a defined geographical radius from the pre-seeded master database.
    """
    mandis = find_nearby_mandis(lat=lat, lon=lon, radius_km=radius, limit=limit)
    return {
        "origin": {"lat": lat, "lon": lon},
        "radius_km": radius,
        "count": len(mandis),
        "mandis": mandis
    }

@router.get("/all")
async def get_all_mandis() -> Dict[str, Any]:
    return {
        "count": len(MANDI_MASTER_DATA),
        "mandis": MANDI_MASTER_DATA
    }
