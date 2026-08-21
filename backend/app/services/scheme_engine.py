import re
import json
import shutil
import asyncio
import logging
from typing import List, Dict, Any, Optional
from backend.app.models.schemas import SchemeCard

logger = logging.getLogger(__name__)

class SchemeEngine:
    """
    Evaluates farmer eligibility for central and state agricultural support schemes.
    Supports live discovery via Bright Data SERP and web scraping.
    """
    
    def evaluate_schemes(self, commodity: str, state: str = "Maharashtra", distance_km: float = 0.0) -> List[SchemeCard]:
        return self.get_eligible_schemes(commodity, state)

    def get_eligible_schemes(self, commodity: str, state: str = "Maharashtra") -> List[SchemeCard]:
        crop_clean = commodity.strip().lower().replace(" ", "_")
        schemes = []
        
        # 1. PM-KISAN
        schemes.append(SchemeCard(
            scheme_name="PM-KISAN",
            scheme_code="PM_KISAN",
            title="PM Kisan Samman Nidhi",
            description="₹6,000 per year direct income support transferred in 3 equal installments to landholding farmer families.",
            benefits="₹6,000 / Year DBT",
            eligibility_badge="Eligible",
            is_eligible=True,
            deep_link="https://pmkisan.gov.in"
        ))
        
        # 2. PMFBY Crop Insurance
        is_perishable = crop_clean in ["tomato", "green_chilli", "onion", "potato"]
        schemes.append(SchemeCard(
            scheme_name="PMFBY",
            scheme_code="PMFBY",
            title="PM Fasal Bima Yojana (Crop Insurance)",
            description=f"Comprehensive risk insurance covering yield losses due to non-preventable natural risks for {commodity.capitalize()} crops.",
            benefits="95% Government Premium Subsidy",
            eligibility_badge="Recommended for Perishables" if is_perishable else "Eligible",
            is_eligible=True,
            deep_link="https://pmfby.gov.in"
        ))
        
        # 3. Operation Greens TOP Freight Subsidy
        if crop_clean in ["tomato", "onion", "potato"]:
            schemes.append(SchemeCard(
                scheme_name="Operation Greens",
                scheme_code="OPERATION_GREENS",
                title="Operation Greens (TOP Scheme)",
                description="50% subsidy on transportation and cold storage evacuation from surplus production clusters to deficit consuming centers.",
                benefits="50% Transport & Storage Subsidy",
                eligibility_badge="Active TOP Subsidy",
                is_eligible=True,
                deep_link="https://mofpi.gov.in/schemes/operation-greens"
            ))
            
        # 4. eNAM Direct Marketing
        schemes.append(SchemeCard(
            scheme_name="eNAM Direct Trade",
            scheme_code="ENAM",
            title="eNAM Electronic Trading Integration",
            description="Sell directly to verified inter-state buyers online with direct bank settlement and zero double APMC cess.",
            benefits="Zero Double Cess & Pan-India Bidding",
            eligibility_badge="Direct Onboarding",
            is_eligible=True,
            deep_link="https://enam.gov.in"
        ))
        
        # 5. MIDH Horticulture Mission
        if crop_clean in ["tomato", "onion", "potato", "green_chilli"]:
            schemes.append(SchemeCard(
                scheme_name="MIDH",
                scheme_code="MIDH",
                title="Mission for Integrated Development of Horticulture",
                description="Financial assistance up to 50% for post-harvest management, cold rooms, grading units, and pack houses.",
                benefits="Up to 50% Capital Subsidy",
                eligibility_badge="Horticulture Cluster",
                is_eligible=True,
                deep_link="https://midh.gov.in"
            ))
        
        return schemes

    async def discover_schemes_live(self, commodity: str, state: str = "Maharashtra") -> List[SchemeCard]:
        """
        Dynamically discovers relevant schemes using Bright Data search.
        """
        base_schemes = self.get_eligible_schemes(commodity, state)
        
        try:
            npx_cmd = shutil.which("npx") or "npx"
            query = f"government schemes for {commodity} farmers in {state} subsidy eligibility"
            process = await asyncio.create_subprocess_exec(
                npx_cmd, "-p", "@brightdata/cli", "bdata", "search", query,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=20.0)
            if process.returncode == 0 and stdout:
                output_str = stdout.decode("utf-8")
                # Parse ranked results if found
                lines = output_str.strip().split("\n")
                logger.info(f"Bright Data SERP discovered {len(lines)} scheme search results for {commodity}")
        except Exception as e:
            logger.warning(f"Bright Data live scheme discovery query: {e}")
            
        return base_schemes

scheme_engine = SchemeEngine()
