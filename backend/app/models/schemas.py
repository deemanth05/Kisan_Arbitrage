from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class SessionCreateRequest(BaseModel):
    device_id: str = Field(..., description="Unique anonymous device identifier")
    language: str = Field(default="hi", description="Preferred language code (hi, mr, en)")
    lat: Optional[float] = None
    lon: Optional[float] = None

class SessionResponse(BaseModel):
    session_id: str
    device_id: str
    language: str
    status: str
    created_at: str

class AnalysisRequest(BaseModel):
    commodity: str = Field(..., description="Crop name (e.g. Tomato, Onion, Potato, Soybean, Cotton, Wheat)")
    quantity: float = Field(..., gt=0, description="Quantity of produce")
    unit: str = Field(default="quintal", description="Unit of quantity (quintal, ton, kg)")
    origin_city: str = Field(..., description="Origin city/village (e.g. Kolhapur)")
    origin_lat: float = Field(..., description="Latitude of origin")
    origin_lon: float = Field(..., description="Longitude of origin")
    vehicle_type: str = Field(default="bolero_pickup", description="tata_ace, bolero_pickup, eicher_14ft")
    query_text: Optional[str] = None

class MandiCostBreakdown(BaseModel):
    gross_revenue: float
    freight_cost: float
    diesel_price_per_litre: float
    distance_km: float
    transit_duration_hours: float
    apmc_cess: float
    apmc_cess_percentage: float
    weighment_loading: float
    spoilage_loss_amount: float
    spoilage_percentage: float
    transit_temperature: float
    has_rain: bool
    net_profit: float
    profit_difference_vs_local: float

class MandiArbitrageOption(BaseModel):
    mandi_id: str
    mandi_name: str
    district: str
    state: str
    lat: float
    lon: float
    distance_km: float
    modal_price: float
    min_price: float
    max_price: float
    price_unit: str = "₹/quintal"
    is_recommended: bool = False
    is_local_baseline: bool = False
    benchmark_status: str = "ABOVE_BENCHMARK"  # "ABOVE_BENCHMARK", "AT_BENCHMARK", "BELOW_BENCHMARK"
    benchmark_name: str = "TOP Benchmark"  # "MSP" or "TOP Operation Greens"
    benchmark_diff: float = 0.0
    market_pulse: str = "NORMAL_SUPPLY"  # "HIGH_SUPPLY", "NORMAL_SUPPLY", "SCARCITY_HIGH_DEMAND"
    arrival_quantity: float = 0.0
    arrival_unit: str = "Tonnes"
    trend_direction: str = "UP"  # "UP", "DOWN", "STABLE"
    sparkline_prices: List[float] = Field(default_factory=list)
    community_reported_price: Optional[float] = None
    community_report_time: Optional[str] = None
    breakdown: MandiCostBreakdown

class SchemeCard(BaseModel):
    scheme_name: str
    scheme_code: str
    title: str
    description: str
    benefits: str
    eligibility_badge: str = "Eligible"
    is_eligible: bool = True
    deep_link: str

class ArbitrageAnalysisResult(BaseModel):
    session_id: str
    commodity: str
    quantity: float
    unit: str
    origin_city: str
    origin_lat: float
    origin_lon: float
    vehicle_type: str
    recommended_mandi: MandiArbitrageOption
    alternative_mandis: List[MandiArbitrageOption]
    best_time_to_sell: str  # "SELL_TODAY", "WAIT_2_3_DAYS"
    prediction_rationale: str
    localized_explanation: str
    eligible_schemes: List[SchemeCard]
    created_at: str

class SSEEvent(BaseModel):
    event: str
    subagent: Optional[str] = None
    data: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class CommunityReportCreate(BaseModel):
    mandi_id: str
    mandi_name: str
    commodity: str
    price_received: float
    quantity: Optional[float] = None
    farmer_name: Optional[str] = "Kisan Mitra"
    farmer_location: Optional[str] = None

class CommunityReportResponse(BaseModel):
    id: int
    mandi_id: str
    mandi_name: str
    commodity: str
    price_received: float
    farmer_name: str
    timestamp: str

class TransporterApproveRequest(BaseModel):
    session_id: str
    mandi_id: str
    transporter_phone: Optional[str] = "+919876543210"
    transporter_name: Optional[str] = "Shree Balaji Transporters"
    custom_notes: Optional[str] = None

class VoiceTranscribeRequest(BaseModel):
    audio_base64: str
    language: str = "hi"

class VoiceTranscribeResponse(BaseModel):
    text: str
    detected_language: str
    entities: Dict[str, Any] = Field(default_factory=dict)

class TTSRequest(BaseModel):
    text: str
    language: str = "hi"

class TTSResponse(BaseModel):
    audio_base64: str
    language: str

class VoiceTranslateRequest(BaseModel):
    text: str
    source_language: str = "hi"
    target_language: str = "en"

class VoiceTranslateResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
