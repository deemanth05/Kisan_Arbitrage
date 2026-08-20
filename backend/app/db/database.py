import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from backend.app.config import settings

Base = declarative_base()

class DBSession(Base):
    __tablename__ = "sessions"
    
    id = Column(String(64), primary_key=True)
    device_id = Column(String(64), index=True)
    language = Column(String(10), default="hi")
    origin_lat = Column(Float, nullable=True)
    origin_lon = Column(Float, nullable=True)
    status = Column(String(32), default="CREATED")
    result_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBCommunityReport(Base) :
    __tablename__ = "community_reports"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mandi_id = Column(String(64), index=True)
    mandi_name = Column(String(128))
    commodity = Column(String(64), index=True)
    price_received = Column(Float)
    quantity = Column(Float, nullable=True)
    farmer_name = Column(String(128), default="Kisan Mitra")
    farmer_location = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Pre-seed initial community ground-truth reports for realism
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(DBCommunityReport))
        if not result.scalars().first():
            sample_reports = [
                DBCommunityReport(
                    mandi_id="mandi_sangli",
                    mandi_name="Sangli APMC",
                    commodity="Tomato",
                    price_received=1850.0,
                    quantity=25.0,
                    farmer_name="Suresh Patil",
                    farmer_location="Miraj",
                    created_at=datetime.utcnow()
                ),
                DBCommunityReport(
                    mandi_id="mandi_pune",
                    mandi_name="Pune APMC",
                    commodity="Tomato",
                    price_received=2180.0,
                    quantity=40.0,
                    farmer_name="Ramesh Jadhav",
                    farmer_location="Bhor",
                    created_at=datetime.utcnow()
                ),
                DBCommunityReport(
                    mandi_id="mandi_kolhapur",
                    mandi_name="Kolhapur APMC",
                    commodity="Tomato",
                    price_received=1720.0,
                    quantity=15.0,
                    farmer_name="Anand Shinde",
                    farmer_location="Hatkanangale",
                    created_at=datetime.utcnow()
                ),
                DBCommunityReport(
                    mandi_id="mandi_lasalgaon",
                    mandi_name="Lasalgaon APMC",
                    commodity="Onion",
                    price_received=2580.0,
                    quantity=50.0,
                    farmer_name="Ganesh Pawar",
                    farmer_location="Niphad",
                    created_at=datetime.utcnow()
                )
            ]
            session.add_all(sample_reports)
            await session.commit()
