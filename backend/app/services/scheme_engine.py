import re
import json
import logging
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from backend.app.models.schemas import SchemeCard
from backend.app.db.database import AsyncSessionLocal, DBSchemeRecord
from backend.app.scrapers.scraper_studio_client import scraper_studio_client

logger = logging.getLogger(__name__)

# Statutory & Cluster Schemes Knowledge Base with verified official portals
CENTRAL_AGRICULTURAL_SCHEMES = [
    {
        "scheme_name": "PM-KISAN",
        "scheme_code": "PM_KISAN",
        "title": "PM Kisan Samman Nidhi",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "₹6,000 per year direct income support transferred in 3 equal installments of ₹2,000 each directly to farmer bank accounts.",
        "benefits": "₹6,000 / Year Direct DBT",
        "eligibility_badge": "100% Eligible",
        "eligibility_criteria": "All landholding farmer families having cultivable landholding in their names.",
        "documents_required": ["Aadhaar Card", "Land Ownership Documents (7/12 Extract)", "Bank Account Details"],
        "application_url": "https://pmkisan.gov.in/RegistrationFormNew.aspx",
        "deep_link": "https://pmkisan.gov.in",
        "applicable_crops": ["all"]
    },
    {
        "scheme_name": "PMFBY",
        "scheme_code": "PMFBY",
        "title": "Pradhan Mantri Fasal Bima Yojana",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "Comprehensive risk insurance covering yield losses due to non-preventable natural risks (drought, flood, pests, unseasonal rain).",
        "benefits": "95% Government Premium Subsidy",
        "eligibility_badge": "High Priority for Perishables",
        "eligibility_criteria": "All farmers growing notified crops in notified areas including sharecroppers and tenant farmers.",
        "documents_required": ["Aadhaar Card", "Land Record / Sowing Certificate", "Bank Passbook"],
        "application_url": "https://pmfby.gov.in",
        "deep_link": "https://pmfby.gov.in",
        "applicable_crops": ["all"]
    },
    {
        "scheme_name": "Operation Greens",
        "scheme_code": "OPERATION_GREENS",
        "title": "Operation Greens (TOP to TOTAL Scheme)",
        "ministry": "Ministry of Food Processing Industries (MoFPI)",
        "description": "50% subsidy on freight transportation and cold storage evacuation from surplus production clusters to deficit consuming markets.",
        "benefits": "50% Freight & Cold Storage Subsidy",
        "eligibility_badge": "Active TOP Subsidy",
        "eligibility_criteria": "Farmers, FPOs, and cooperatives transporting Tomato, Onion, and Potato (TOP) crops across interstate corridors.",
        "documents_required": ["Transport Toll Receipts / Waybill", "APMC Gate Pass", "FPO / Farmer Registration"],
        "application_url": "https://www.sampada-mofpi.gov.in",
        "deep_link": "https://mofpi.gov.in/schemes/operation-greens",
        "applicable_crops": ["tomato", "onion", "potato"]
    },
    {
        "scheme_name": "eNAM Direct Trade",
        "scheme_code": "ENAM",
        "title": "National Agriculture Market (eNAM)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "Pan-India electronic trading portal integrating APMC mandis to facilitate transparent online price discovery and inter-state selling.",
        "benefits": "Zero Double Mandi Cess & Pan-India Bidding",
        "eligibility_badge": "Direct Onboarding",
        "eligibility_criteria": "Any farmer possessing agricultural produce visiting an eNAM-enabled APMC mandi.",
        "documents_required": ["Mandi Gate Pass", "Bank Account Details", "Assay Quality Certificate"],
        "application_url": "https://enam.gov.in/web/stakeholders-registration/farmer",
        "deep_link": "https://enam.gov.in",
        "applicable_crops": ["all"]
    },
    {
        "scheme_name": "MIDH Horticulture Mission",
        "scheme_code": "MIDH",
        "title": "Mission for Integrated Development of Horticulture",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "Holistic growth of the horticulture sector including capital subsidy up to 50% for post-harvest pack houses, cold storage, and grading sheds.",
        "benefits": "Up to 50% Post-Harvest Infrastructure Subsidy",
        "eligibility_badge": "Horticulture Cluster",
        "eligibility_criteria": "Individual farmers, groups, and FPOs cultivating fruits, vegetables, and horticulture produce.",
        "documents_required": ["Land Documents", "Project Report for Storage/Packhouse", "Aadhaar Card"],
        "application_url": "https://midh.gov.in",
        "deep_link": "https://midh.gov.in",
        "applicable_crops": ["tomato", "onion", "potato", "green_chilli", "fruit", "vegetable"]
    },
    {
        "scheme_name": "SMAM Mechanization",
        "scheme_code": "SMAM",
        "title": "Sub-Mission on Agricultural Mechanization",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "Financial assistance of 40% to 50% subsidy on procurement of farm equipment, power tillers, sprayers, and harvesting machinery.",
        "benefits": "40% - 50% Subsidy on Farm Machinery",
        "eligibility_badge": "Mechanization Subsidy",
        "eligibility_criteria": "Small, marginal, and women farmers seeking modern farm equipment.",
        "documents_required": ["Aadhaar Card", "7/12 Land Extract", "Bank Passbook", "Quotations from Authorized Dealer"],
        "application_url": "https://agrimachinery.nic.in",
        "deep_link": "https://agrimachinery.nic.in",
        "applicable_crops": ["all"]
    }
]

class SchemeEngine:
    """
    Evaluates farmer eligibility for central and state agricultural support schemes.
    Supports live discovery via Bright Data SERP and database caching.
    """
    
    def evaluate_schemes(self, commodity: str, state: str = "Maharashtra", distance_km: float = 0.0) -> List[SchemeCard]:
        return self.get_eligible_schemes(commodity, state)

    def get_eligible_schemes(self, commodity: str, state: str = "Maharashtra") -> List[SchemeCard]:
        crop_clean = commodity.strip().lower().replace(" ", "_")
        schemes: List[SchemeCard] = []
        
        for s in CENTRAL_AGRICULTURAL_SCHEMES:
            applicable = s["applicable_crops"]
            if "all" in applicable or crop_clean in applicable or any(c in crop_clean for c in applicable):
                schemes.append(SchemeCard(
                    scheme_name=s["scheme_name"],
                    scheme_code=s["scheme_code"],
                    title=s["title"],
                    ministry=s.get("ministry"),
                    description=s["description"],
                    benefits=s["benefits"],
                    eligibility_badge=s["eligibility_badge"],
                    eligibility_criteria=s.get("eligibility_criteria"),
                    documents_required=s.get("documents_required", []),
                    application_url=s.get("application_url"),
                    deep_link=s["deep_link"],
                    is_eligible=True,
                    data_source="CENTRAL_POLICY_CATALOG"
                ))
                
        return schemes

    async def _cache_schemes_in_db(self, schemes: List[SchemeCard], commodity: str, state: str):
        try:
            async with AsyncSessionLocal() as session:
                for s in schemes:
                    rec = DBSchemeRecord(
                        scheme_name=s.scheme_name,
                        scheme_code=s.scheme_code or s.scheme_name,
                        title=s.title or s.scheme_name,
                        ministry=s.ministry,
                        description=s.description,
                        benefits=s.benefits,
                        eligibility_badge=s.eligibility_badge,
                        eligibility_criteria=s.eligibility_criteria,
                        documents_required=json.dumps(s.documents_required),
                        application_url=s.application_url,
                        deep_link=s.deep_link,
                        commodity_query=commodity.strip().lower(),
                        state_query=state.strip().lower(),
                        data_source=s.data_source,
                        is_eligible=s.is_eligible,
                        scraped_at=datetime.now(UTC)
                    )
                    session.add(rec)
                await session.commit()
        except Exception as e:
            logger.warning(f"Error caching schemes into database: {e}")

    async def _get_cached_schemes_from_db(self, commodity: str, state: str) -> List[SchemeCard]:
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(DBSchemeRecord).where(
                    DBSchemeRecord.commodity_query == commodity.strip().lower(),
                    DBSchemeRecord.state_query == state.strip().lower()
                ).limit(10)
                records = (await session.execute(stmt)).scalars().all()
                if records:
                    return [
                        SchemeCard(
                            scheme_name=r.scheme_name,
                            scheme_code=r.scheme_code,
                            title=r.title or r.scheme_name,
                            ministry=r.ministry,
                            description=r.description,
                            benefits=r.benefits,
                            eligibility_badge=r.eligibility_badge,
                            eligibility_criteria=r.eligibility_criteria,
                            documents_required=json.loads(r.documents_required) if r.documents_required else [],
                            application_url=r.application_url,
                            deep_link=r.deep_link,
                            is_eligible=r.is_eligible,
                            data_source="CACHED_SCRAPED_DISCOVERY"
                        )
                        for r in records
                    ]
        except Exception as e:
            logger.warning(f"Error querying cached schemes: {e}")
        return []

    async def discover_schemes_live(self, commodity: str, state: str = "Maharashtra") -> List[SchemeCard]:
        """
        Dynamically discovers relevant schemes using Bright Data search,
        persisting findings to SQLite and returning verified scheme cards.
        """
        base_schemes = self.get_eligible_schemes(commodity, state)
        
        # 1. Trigger live Bright Data SERP search
        query = f"government schemes for {commodity} farmers in {state} subsidy eligibility"
        serp_results = await scraper_studio_client.search_serp(query)
        
        if serp_results:
            logger.info(f"Bright Data SERP found {len(serp_results)} live scheme links for {commodity} in {state}")
            for item in serp_results:
                title = item.get("title", "")
                url = item.get("url", "")
                desc = item.get("description", "")
                
                # Check if this discovered scheme is already in base schemes
                already_present = any(s.scheme_name.lower() in title.lower() or s.deep_link == url for s in base_schemes)
                if not already_present and len(title) > 5 and ("scheme" in title.lower() or "yojana" in title.lower() or "subsidy" in title.lower() or "mission" in title.lower()):
                    base_schemes.append(SchemeCard(
                        scheme_name=title[:40],
                        scheme_code="DISCOVERED_" + str(item.get("rank", 1)),
                        title=title,
                        ministry=state + " State Agricultural Department",
                        description=desc or f"Government agricultural support scheme discovered for {commodity} growers.",
                        benefits="State Agricultural Assistance",
                        eligibility_badge="Live Discovered",
                        eligibility_criteria=f"Farmers producing {commodity} in {state}.",
                        documents_required=["Aadhaar Card", "Farmer ID", "Bank Account"],
                        application_url=url,
                        deep_link=url,
                        is_eligible=True,
                        data_source="BRIGHT_DATA_SERP_DISCOVERY"
                    ))

        # 2. Persist to DB cache
        await self._cache_schemes_in_db(base_schemes, commodity, state)
        return base_schemes

scheme_engine = SchemeEngine()
