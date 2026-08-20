from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.models.schemas import CommunityReportCreate, CommunityReportResponse
from backend.app.db.database import AsyncSessionLocal, DBCommunityReport

router = APIRouter(prefix="/api/v1/community", tags=["Community Ground Truth"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/report", response_model=CommunityReportResponse)
async def submit_price_report(
    req: CommunityReportCreate,
    db: AsyncSession = Depends(get_db)
):
    report = DBCommunityReport(
        mandi_id=req.mandi_id,
        mandi_name=req.mandi_name,
        commodity=req.commodity,
        price_received=req.price_received,
        quantity=req.quantity,
        farmer_name=req.farmer_name or "Kisan Mitra",
        farmer_location=req.farmer_location,
        created_at=datetime.utcnow()
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return CommunityReportResponse(
        id=report.id,
        mandi_id=report.mandi_id,
        mandi_name=report.mandi_name,
        commodity=report.commodity,
        price_received=report.price_received,
        farmer_name=report.farmer_name,
        timestamp=report.created_at.isoformat()
    )

@router.get("/reports", response_model=List[CommunityReportResponse])
async def list_community_reports(
    commodity: Optional[str] = Query(None),
    mandi_id: Optional[str] = Query(None),
    limit: int = Query(20),
    db: AsyncSession = Depends(get_db)
):
    query = select(DBCommunityReport).order_by(desc(DBCommunityReport.created_at)).limit(limit)
    if commodity:
        query = query.where(DBCommunityReport.commodity.ilike(f"%{commodity}%"))
    if mandi_id:
        query = query.where(DBCommunityReport.mandi_id == mandi_id)
        
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return [
        CommunityReportResponse(
            id=r.id,
            mandi_id=r.mandi_id,
            mandi_name=r.mandi_name,
            commodity=r.commodity,
            price_received=r.price_received,
            farmer_name=r.farmer_name,
            timestamp=r.created_at.isoformat()
        )
        for r in reports
    ]
