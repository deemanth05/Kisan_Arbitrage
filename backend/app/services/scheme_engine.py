import logging
from typing import List, Dict, Any
from backend.app.models.schemas import SchemeCard

logger = logging.getLogger(__name__)

class SchemeEngine:
    """
    Evaluates farmer eligibility for central and state agricultural support schemes.
    """
    
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
        
        return schemes

scheme_engine = SchemeEngine()
