# Product Requirements Document (PRD): KisanArbitrage

## 1. Product Vision & Problem Statement

**Vision:**  
Empower Indian smallholder farmers to maximize their take-home profit by making intelligent, data-driven decisions on where and when to sell their produce. KisanArbitrage acts as an autonomous AI agent that calculates true net arbitrage across alternative mandis (wholesale markets) by accounting for real-time prices, scraped live diesel-adjusted freight costs, statutory APMC taxes, and weather-driven ICAR spoilage risks.

**Problem Statement:**  
Farmers typically sell their harvest at the nearest local mandi because they lack transparent visibility into alternative markets and cannot compute net profitability. Even when prices in a distant mandi appear ₹400/quintal higher, determining whether that margin survives transportation costs, tolls, APMC cess, and produce decay during transit is complex and error-prone.

Existing agricultural applications fail because:
1. They act as passive price lookups without computing net profit math.
2. They ignore logistics economics (vehicle class, fuel inflation, empty return factors).
3. They overlook weather-induced transit spoilage (high heat/rain rotting perishable crops).
4. They lack voice interfaces for farmers with low literacy.
5. They miss crucial economic context like MSP (Minimum Support Price) and TOP (Operation Greens) fair benchmark prices.

---

## 2. Target Audience / Personas

### Persona 1: Ramesh (Tomato Farmer, Kolhapur)
- **Profile:** Smallholder farmer with 2 acres of tomato crops (highly perishable produce).
- **Pain Points:** Tomatoes spoil rapidly under heat >35°C. High transportation costs eat into margins. Needs quick, definitive answers on whether to sell locally or truck to Pune/Sangli today.
- **Tech Savvy:** Low to medium. Prefers voice-based interactions and WhatsApp notifications.

### Persona 2: Suresh (Onion Farmer, Nashik)
- **Profile:** Mid-sized farmer dealing with semi-perishable bulk goods (Onion/Potato).
- **Pain Points:** Needs to understand storage vs. immediate sale trade-offs. Wants to know historical price trends and inter-state eNAM prices.
- **Tech Savvy:** Medium. Prefers clean mobile/web UI in Marathi.

### Persona 3: Basavaraj (Vegetable Farmer, Belgaum)
- **Profile:** Kannada/Marathi-speaking farmer located near the Maharashtra-Karnataka border, with access to APMCs in both states.
- **Pain Points:** Cross-state mandi price disparity and language barriers. Needs comparison between Belgaum (KA) and Kolhapur/Sangli (MH) mandis.
- **Tech Savvy:** Low. Relies heavily on voice queries in Kannada or Hindi.

---

## 3. Features (The "What")

### 3.1. Core Arbitrage Engine
- **F1: Net Profit Calculation (P0):**
  $$\text{Net Profit} = (\text{Mandi Price} \times \text{Quantity}) - (\text{Freight Cost} + \text{APMC Cess} + \text{Weighment/Loading} + \text{Spoilage Loss})$$
- **F2: Ranked Recommendations (P0):** Display top mandi options sorted by highest net profit, clearly highlighting the additional gain over the local baseline.
- **F3: Transporter Dispatch via WhatsApp (P0):** Trigger a Twilio WhatsApp message to local transporters with pickup details — strictly after farmer approval.
- **F4: Deterministic Python Math Engine (P0):** Compute all financial formulas and spoilage loss percentages in native Python, guaranteeing mathematical precision with zero LLM hallucination and sub-millisecond execution.

### 3.2. Voice & Language
- **F9: Voice Input via Bhashini & WebSpeech (P0):** 
  - Integration with Bhashini for Hindi, Marathi, and Kannada speech recognition.
  - Automatic fallback to Web Speech API and manual form inputs for 100% uptime.
  - TTS (Text-to-Speech) reads out the final recommendation and rationale in the farmer's native tongue.
- **F19: Multi-Language Agent Explanations (P0):**
  - All reasoning, cost breakdowns, and conversational summaries presented seamlessly in the selected language.

### 3.3. Market & Pricing Intelligence (Bright Data Powered)
- **F10: MSP & TOP Benchmark Comparison (P0):**
  - Grains/Pulses/Oilseeds: Compares against Government Minimum Support Price (MSP).
  - Perishables (Tomato, Onion, Potato): Compares against Ministry Operation Greens TOP fair benchmark rates.
  - Displayed as trust badges: `✅ ₹400 ABOVE BENCHMARK` or `⚠️ BELOW BENCHMARK`.
- **F11: 7-Day & 30-Day Price Sparklines (P1):**
  - Visual sparkline chart on each mandi card showing 7-day historical price movement.
- **F12: Market Pulse (Arrival Volume Intelligence) (P1):**
  - Real-time arrival quantities scraped from MSAMB/Agmarknet.
  - High arrivals trigger an oversupply warning; low arrivals signal high-demand scarcity.
- **F16: Predictive "Best Time to Sell" Intelligence (P1):**
  - Evaluates 7-day price momentum and route spoilage to recommend "Sell Today" vs "Wait 2-3 Days".
- **F17: Community Price Reports (P2):**
  - Farmers report actual transaction prices received at mandis to provide verified ground truth.
- **F18: eNAM Inter-State Scraper (P1):**
  - Real-time scraper on the eNAM dashboard (`enam.gov.in`) using Bright Data to capture national inter-state prices.

### 3.4. Logistics & Weather Spoilage
- **F13: ICAR-CIPHET Perishable Spoilage Model (P0):**
  - Applies scientifically grounded \(Q_{10}\) physiological respiration loss curves.
  - Combines Open-Meteo hourly route temperatures and rainfall with transit duration from OpenRouteService.
  - Example: Tomatoes face 0.5%/hr weight and quality loss when ambient temperatures exceed 35°C during transit.
- **F14: Dynamic Mandi Discovery (P0):**
  - Auto-discovers candidate APMC mandis within a configurable radius (50/100/150 km) using GPS coordinates and pre-seeded database of 50+ major mandis.
- **F20: Live District Diesel Scraping (P0):**
  - Scrapes daily city/district diesel rates to ground transport cost calculations in real fuel prices.

### 3.5. Government Scheme Support
- **F15: Government Scheme Eligibility (P2):**
  - Checks farmer profile against PM-KISAN, PMFBY (Crop Insurance), and eNAM direct onboarding incentives.

---

## 4. Multi-Agent Swarm Architecture

The intelligence layer uses **Google Gemini 2.5 Flash** orchestrating 4 specialized subagent tasks:
1. **Root Orchestrator:** Parses farmer voice/text input, queries nearby mandis, triggers parallel subagents, and synthesizes final localized recommendation.
2. **Subagent A (Market Intel):** Queries MSAMB, Agmarknet, and eNAM scrapers for real-time rates, arrivals, and 7-day trends.
3. **Subagent B (Logistics Intel):** Queries live diesel scraper, vehicle matrix, and OpenRouteService for distance and toll calculations.
4. **Subagent C (Weather Risk):** Queries Open-Meteo for route heat/precipitation profiles to compute ICAR spoilage risk.
5. **Subagent D (Scheme Policy):** Evaluates farmer profile against central and state agricultural schemes.
6. **Deterministic Math Engine:** Calculates final net arbitrage and ranked comparison in Python.
7. **Human Approval Gate:** Presents the optimal option to the farmer before triggering transporter dispatch.

---

## 5. User Journey & Flow

1. **Voice Query:** Farmer speaks: *"मेरे पास 20 क्विंटल टमाटर है, कहाँ बेचूं?"*
2. **Transcription & Entity Extraction:** Bhashini transcribes and extracts: `Crop: Tomato`, `Quantity: 20 Quintals`, `Location: Kolhapur`.
3. **Parallel Intelligence Gathering:** FastAPI dispatches scrapers, Open-Meteo, OpenRouteService, and the Arbitrage Engine.
4. **Real-time SSE Streaming:** Mobile/Web UI shows live progress animations (`Market Intel...`, `Logistics...`, `Weather Risk...`).
5. **Hero Comparison Screen:** Farmer sees ranked mandi cards with net profit, benchmark badges, sparklines, arrival pulse, and spoilage warnings.
6. **Voice Readout:** Bhashini TTS reads out the summary in Hindi/Marathi.
7. **Approval Gate:** Farmer taps "Approve & Notify Transporter" -> WhatsApp message sent to transporter.

---

## 6. Tech Stack & Cost ($0/Month)

| Component | Technology | Cost (Hackathon) |
|-----------|------------|------------------|
| **Client** | Flutter 3.x (Mobile & Web) | Free / Open Source |
| **Backend API** | FastAPI (Python 3.11+) | Free Tier (Railway / Render) |
| **Agent LLM** | Google Gemini 2.5 Flash | Free Tier (15 RPM, 1M tokens/day) |
| **Scrapers** | Bright Data Scraping Browser & Web Unlocker | Hackathon Credits |
| **Language AI** | Bhashini API (with WebSpeech fallback) | Free (Government Platform) |
| **Weather API** | Open-Meteo | Free (No API key required) |
| **Routing API** | OpenRouteService | Free Tier (40 req/min) |
| **Database** | SQLite / Supabase | Free Tier |
| **Transporter SMS/WA** | Twilio WhatsApp Sandbox | Free Tier |
| **Total** | | **$0 / month** |

---

## 7. Risks & Mitigations

1. **Mandi Data Fluctuations & Scraper Changes:**
   - *Risk:* Portal DOM structure changes.
   - *Mitigation:* Bright Data Web Unlocker & AI-driven element extraction handle dynamic structures resiliently.
2. **Bhashini Latency:**
   - *Risk:* Government voice API latency spikes.
   - *Mitigation:* Web Speech API in-browser fallback and manual form editing support.
3. **Mathematical Accuracy:**
   - *Risk:* LLM arithmetic errors.
   - *Mitigation:* All financial math and spoilage equations are executed in deterministic Python modules, completely isolated from LLM text generation.
