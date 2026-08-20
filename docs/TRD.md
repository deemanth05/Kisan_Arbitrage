# Technical Requirements Document (TRD)
## KisanArbitrage

### 1. Overview
KisanArbitrage is an autonomous mandi price arbitrage and freight optimization platform for Indian farmers. It computes the net profitability of selling produce across alternative APMC mandis by analyzing real-time prices, live fuel-adjusted freight logistics, statutory APMC taxes, and weather-driven ICAR post-harvest spoilage risks.

Built for the **Scrape-Verse Hackathon** powered by **Bright Data**.

---

### 2. Architecture & Tech Stack

#### Multi-Agent Orchestrator & Backend (FastAPI - Python 3.11+)
- **Framework**: FastAPI (Python 3.11+) with native asynchronous routing & SSE streaming.
- **LLM Engine**: Google Gemini 2.5 Flash via `google-generativeai` SDK for natural language understanding, intent extraction, multi-agent reasoning, and Indic synthesis.
- **Deterministic Math & Spoilage Engine**: Native Python mathematical computation engine (`arbitrage_engine.py`, `logistics_engine.py`, `spoilage_engine.py`) ensuring zero arithmetic hallucination and sub-millisecond execution.
- **Database**: SQLite (local development & caching) with pre-seeded `mandi_master` (50+ APMCs across Maharashtra & Karnataka) and Supabase PostgreSQL client (`supabase-py`) for cloud sync and community reports.
- **Voice/Language Services**: Bhashini API (ASR, Translation, TTS) with automatic fallback to browser Web Speech API.

#### Client Layer (Flutter 3.x - Dart)
- **Platforms**: Mobile (Android/iOS) and Web (`flutter build web` for direct browser judging).
- **State Management**: Riverpod (`flutter_riverpod`).
- **Networking**: `dio` (REST) and `fetch_client` / `http` chunked stream for real-time SSE.
- **Charts**: `fl_chart` (7-day sparklines).
- **Audio & Speech**: `record` and `just_audio`.
- **Location**: `geolocator` and `geocoding`.

#### Real-Time Scraping Layer (Bright Data)
- **Scraper Infrastructure**: Bright Data Scraping Browser & Web Unlocker.
- **Dedicated Scrapers**:
  1. **MSAMB & Agmarknet Scraper**: Scrapes daily arrival bulletins, min/max/modal prices across APMCs.
  2. **eNAM National Trade Scraper**: Scrapes dynamic trade data and inter-state auctions from `enam.gov.in`.
  3. **Live Fuel Rate Scraper**: Scrapes daily district diesel rates from `mypetrolprice.com` / `goodreturns.in` for accurate freight indexation.
  4. **APMC Statutory Cess Scraper**: Scrapes state agricultural marketing board schedules for market fees and cess.

#### External Real-Time Services
- **Weather & Transit Climate**: Open-Meteo API (hourly temperature, relative humidity, precipitation along route coordinates).
- **Logistics Matrix**: OpenRouteService API (road distance and driving duration).
- **Transporter Dispatch**: Twilio WhatsApp Sandbox (human approval gated notifications).

---

### 3. Service Communication Architecture

| Service | Port | Protocol | Called By | Purpose |
|---------|------|----------|-----------|---------|
| Flutter Client | N/A | HTTPS + SSE | End User | Mobile & Web Interface |
| FastAPI Gateway | 8000 | HTTP / SSE | Flutter | Central Proxy & Intelligence Engine |
| Gemini 2.5 Agent | Cloud | HTTPS SDK | FastAPI | Multi-Agent Orchestrator |
| Bright Data Scrapers | Cloud | HTTPS Proxy | FastAPI | Real-Time Mandi, eNAM & Fuel Extraction |
| Open-Meteo | Cloud | HTTPS REST | FastAPI | Route Weather Forecast |
| OpenRouteService | Cloud | HTTPS REST | FastAPI | Road Distance Matrix |
| Bhashini AI | Cloud | HTTPS REST | FastAPI | Indic ASR & TTS |
| Twilio Sandbox | Cloud | HTTPS REST | FastAPI | WhatsApp Transporter Alerts |
| Supabase / SQLite | Local/Cloud | SQL / REST | FastAPI | Mandi Master & Community Data |

---

### 4. SSE Stream Event Specification

FastAPI streams real-time agent progression to Flutter via `GET /api/v1/sessions/{session_id}/stream`:

```json
{
  "event": "subagent.tool_call",
  "subagent": "Logistics Intel",
  "data": {
    "tool": "scrape_diesel_rates",
    "status": "in_progress",
    "message": "Scraping live Kolhapur-Pune diesel prices via Bright Data..."
  },
  "timestamp": "2026-08-18T20:00:00Z"
}
```

| SSE Event | Triggered When | Client UI Action |
|-----------|----------------|------------------|
| `subagent.started` | Subagent initializes | Turn subagent icon to pulsing amber |
| `subagent.tool_call` | Tool or scraper invoked | Display current scraper/API status under agent card |
| `subagent.completed` | Subagent data collected | Indicator turns green checkmark |
| `engine.calculating` | Deterministic Python engine starts | Show "Computing net arbitrage with live diesel & ICAR curves..." |
| `turn.paused` | Optimal route requires confirmation | Opens Screen 6 (Transporter Approval Gate) |
| `turn.completed` | Analysis completed | Renders Screen 4 (Comparison Hero Screen) |
| `tool.completed` | Twilio WhatsApp sent | Navigates to Screen 7 (Success & Confirmation) |
| `error` | Any unrecoverable issue | Shows graceful error banner with retry option |

---

### 5. API Endpoints (FastAPI)

#### Core Session & Analysis Routes
- `POST /api/v1/sessions` — Initialize an analysis session (accepts `device_id`, `language`, `lat`, `lon`).
- `POST /api/v1/sessions/{session_id}/analyze` — Submit farmer query (voice transcription or text), kicks off async pipeline.
- `GET /api/v1/sessions/{session_id}/stream` — SSE endpoint streaming real-time agent execution events.
- `POST /api/v1/sessions/{session_id}/approve` — Approve transporter notification (triggers Twilio WhatsApp dispatch).
- `GET /api/v1/sessions/{session_id}/result` — Fetch complete structured arbitrage result.

#### Mandi & Pricing Data
- `GET /api/v1/mandis/nearby?lat={lat}&lon={lon}&radius={radius}` — Radius discovery of nearby APMCs from pre-seeded database.
- `GET /api/v1/prices/history?commodity={commodity}&market={market}&days={days}` — 7-day sparkline and 30-day historical data.
- `GET /api/v1/benchmark/{commodity}` — Current MSP (grains/pulses) or Operation Greens TOP benchmark price (vegetables).

#### Community Intel
- `POST /api/v1/community/report` — Farmer submits ground-truth realized selling price.
- `GET /api/v1/community/reports?mandi={mandi}&commodity={commodity}` — List recent community reports.

#### Voice & Speech Services
- `POST /api/v1/voice/transcribe` — Accepts audio base64, returns transcribed Indic text.
- `POST /api/v1/voice/tts` — Accepts localized text, returns audio stream or base64.
- `POST /api/v1/voice/translate` — Translates text between Hindi, Marathi, and English.

---

### 6. Data Models (Pydantic)

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class SessionCreateRequest(BaseModel):
    device_id: str
    language: str = "hi"
    lat: Optional[float] = None
    lon: Optional[float] = None

class AnalysisRequest(BaseModel):
    query_text: Optional[str] = None
    commodity: str
    quantity: float
    unit: str = "quintal"
    origin_city: str
    origin_lat: float
    origin_lon: float
    vehicle_type: str = "bolero_pickup" # tata_ace, bolero_pickup, eicher_14ft

class MandiCostBreakdown(BaseModel):
    gross_revenue: float
    freight_cost: float
    diesel_price_per_litre: float
    distance_km: float
    transit_duration_hours: float
    apmc_cess: float
    weighment_loading: float
    spoilage_loss_amount: float
    spoilage_percentage: float
    transit_temperature: float
    net_profit: float
    profit_difference_vs_local: float

class MandiArbitrageOption(BaseModel):
    mandi_id: str
    mandi_name: str
    state: str
    distance_km: float
    modal_price: float
    price_unit: str = "₹/quintal"
    is_recommended: bool
    benchmark_status: str # "ABOVE_BENCHMARK", "AT_BENCHMARK", "BELOW_BENCHMARK"
    benchmark_diff: float
    market_pulse: str # "HIGH_SUPPLY", "NORMAL_SUPPLY", "SCARCITY_HIGH_DEMAND"
    arrival_quantity: float
    trend_direction: str # "UP", "DOWN", "STABLE"
    sparkline_prices: List[float]
    community_reported_price: Optional[float] = None
    breakdown: MandiCostBreakdown

class ArbitrageAnalysisResult(BaseModel):
    session_id: str
    commodity: str
    quantity: float
    origin: str
    recommended_mandi: MandiArbitrageOption
    alternative_mandis: List[MandiArbitrageOption]
    best_time_to_sell: str # "SELL_TODAY", "WAIT_2_3_DAYS"
    prediction_rationale: str
    localized_explanation: str
    eligible_schemes: List[dict]
```

---

### 7. Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Google Gemini 2.5 Flash LLM API key |
| `BRIGHT_DATA_SCRAPING_BROWSER_URL` | Bright Data Scraping Browser WebSocket/Proxy endpoint |
| `BRIGHT_DATA_WEB_UNLOCKER_URL` | Bright Data Web Unlocker proxy URL |
| `OPEN_ROUTE_API_KEY` | OpenRouteService routing API key |
| `BHASHINI_API_KEY` | Bhashini language services API key (optional, fallback to WebSpeech) |
| `BHASHINI_USER_ID` | Bhashini user ID |
| `TWILIO_ACCOUNT_SID` | Twilio WhatsApp integration SID |
| `TWILIO_AUTH_TOKEN` | Twilio WhatsApp integration Token |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp sender number |
| `SUPABASE_URL` | Supabase PostgreSQL project URL |
| `SUPABASE_ANON_KEY` | Supabase public key |
| `DATABASE_URL` | Local SQLite / PostgreSQL connection string |
