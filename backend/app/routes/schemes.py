from fastapi import APIRouter, Query
from typing import List, Optional
from backend.app.services.scheme_engine import scheme_engine
from backend.app.models.schemas import SchemeCard

router = APIRouter(prefix="/api/v1/schemes", tags=["Government Schemes"])

@router.get("/discover", response_model=List[SchemeCard])
async def discover_schemes(
    commodity: str = Query("Tomato", description="Crop commodity name"),
    state: str = Query("Maharashtra", description="State name")
):
    """
    Discovers relevant central and state agricultural schemes for a given crop and state,
    powered by Bright Data discovery.
    """
    return await scheme_engine.discover_schemes_live(commodity=commodity, state=state)
