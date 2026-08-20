from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any
from backend.app.scrapers.mandi_scraper import mandi_scraper
from backend.app.services.msp_engine import msp_engine
from backend.app.scrapers.enam_scraper import enam_scraper

router = APIRouter(prefix="/api/v1/prices", tags=["Prices & Benchmarks"])

@router.get("/history")
async def get_price_history(
    commodity: str = Query("Tomato", description="Commodity name"),
    market: str = Query("Pune", description="APMC Market name"),
    days: int = Query(7, description="Number of historical days")
) -> Dict[str, Any]:
    rates = await mandi_scraper.get_mandi_rates(commodity, market)
    return {
        "commodity": commodity,
        "market": market,
        "days": days,
        "modal_price": rates["modal_price"],
        "trend_direction": rates["trend_direction"],
        "sparkline": rates["sparkline_prices"]
    }

@router.get("/benchmark/{commodity}")
async def get_benchmark_price(commodity: str) -> Dict[str, Any]:
    rates = await mandi_scraper.get_mandi_rates(commodity, "Pune")
    return msp_engine.evaluate_benchmark(commodity, rates["modal_price"])

@router.get("/enam/{commodity}")
async def get_enam_data(commodity: str) -> Dict[str, Any]:
    return await enam_scraper.get_enam_trade_data(commodity)
