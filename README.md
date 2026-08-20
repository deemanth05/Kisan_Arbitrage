# 🌾 KisanArbitrage

> **An autonomous AI agent that tells Indian farmers WHERE to sell, not just what the price is.**

[![Scrape-Verse Hackathon](https://img.shields.io/badge/Hackathon-Scrape--Verse%20Aug%2017--23-brightgreen)](https://www.wemakedevs.org/hackathons/scrape-verse)
[![Bright Data](https://img.shields.io/badge/Scraping-Bright%20Data-blue)](https://brightdata.com)
[![Stack](https://img.shields.io/badge/Stack-Flutter%20%7C%20FastAPI%20%7C%20Gemini%202.5%20%7C%20Bhashini-orange)]()
[![Cost](https://img.shields.io/badge/Infrastructure%20Cost-%240%2Fmonth-success)]()

---

## The Problem

Indian smallholder farmers (86% of all holdings) lose **20–35% of potential revenue** because they default to selling at the nearest local mandi. While tomato prices might be ₹400/quintal higher in Pune than Kolhapur, farmers cannot easily calculate the net arbitrage:

- **What does the truck actually cost?** (Real fuel prices, distance, return trip factor, driver charges)
- **What are the APMC market cess, weighment, and toll charges?**
- **Will the produce spoil in transit under the current heatwave or rain?**
- **Is the price above the Government MSP / TOP benchmark rate?**
- **Should they sell today or wait 3 days?**

Existing apps act as passive price lists without doing the net profit math. **KisanArbitrage computes the true net profit across all accessible markets in real time.**

---

## What It Does

A farmer speaks into their phone in Hindi, Marathi, or English:
> *"मेरे पास 20 क्विंटल टमाटर है, कहाँ बेचूं?"*  
> *("I have 20 quintals of tomatoes, where should I sell?")*

Within seconds, an autonomous multi-agent system:

1. **Scrapes Live Mandi Prices & Arrivals** from MSAMB & Agmarknet using **Bright Data**.
2. **Scrapes Inter-State Prices** from the **eNAM** national trading portal.
3. **Calculates Real-World Freight Rates** by scraping live district-level diesel prices + OpenRouteService routing.
4. **Calculates Spoilage Risk** using **ICAR-CIPHET post-harvest loss curves** combined with real-time route weather from Open-Meteo.
5. **Computes Exact Net Profit** in a deterministic, zero-hallucination Python calculation engine.
6. **Recommends** the optimal mandi with complete cost transparency in the farmer's native language.
7. **Notifies the Transporter** via WhatsApp Sandbox — only after the farmer approves.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Flutter Client (Mobile & Web)                  │
│       Voice Input (Bhashini/WebSpeech) • SSE Stream         │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / SSE
┌──────────────────────────────▼──────────────────────────────┐
│                 FastAPI Unified Backend                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │   Gemini 2.5 Flash Multi-Agent Orchestrator           │  │
│  │   • Market Intel  • Logistics Intel                   │  │
│  │   • Weather Risk  • Scheme & Policy Intel             │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │   Deterministic Python Arbitrage Engine (Zero Error)  │  │
│  │   • Real Freight Model (Diesel + Mileage + Bata)      │  │
│  │   • ICAR-CIPHET Spoilage Equation                     │  │
│  │   • APMC Statutory Cess & Market Fee Rates            │  │
│  │   • MSP & TOP Benchmark Validation                    │  │
│  └───────────────────────────────────────────────────────┘  │
│                              │                              │
│         Bhashini AI  │  Supabase / SQLite (50+ APMCs)       │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
┌───────────────▼──────────────┐ ┌────────────▼───────────────┐
│  Bright Data Scraping Engine │ │   External Real-Time APIs  │
│  • MSAMB & Agmarknet Scraper │ │   • Open-Meteo (Weather)   │
│  • eNAM Trade Portal Scraper │ │   • OpenRouteService       │
│  • Live Diesel Rate Scraper  │ │   • Twilio WhatsApp        │
└──────────────────────────────┘ └────────────────────────────┘
```

---

## Key Differentiators

| Feature | Generic Agri Apps | KisanArbitrage |
|---------|-------------------|----------------|
| **Net Profit Calculation** | ❌ Raw price lookup only | ✅ **True Net Arbitrage** (Revenue − Freight − Cess − Spoilage) |
| **Real Freight Modeling** | ❌ None or arbitrary estimates | ✅ **Scraped Live Diesel + Road Distance + Vehicle Class** |
| **Scientific Spoilage Model** | ❌ Ignored | ✅ **ICAR-CIPHET \(Q_{10}\) Temperature & Rain Loss Curves** |
| **Voice-First Indic Support** | ❌ English/Text only | ✅ **Bhashini ASR & TTS** (Hindi, Marathi, English) |
| **MSP & TOP Benchmarking** | ❌ No context | ✅ **Flags Below-MSP & Operation Greens Fair Prices** |
| **Predictive Best Time to Sell**| ❌ No predictions | ✅ **7-Day Trend & Arrival Scarcity/Oversupply Pulse** |
| **Transporter Dispatch** | ❌ None | ✅ **WhatsApp Dispatch with Human Approval Gate** |
| **Community Ground Truth** | ❌ None | ✅ **Farmer-Submitted Realized Price Feed** |
| **Infrastructure Cost** | High | ✅ **$0/month (100% Free Tiers / Credits)** |

---

## Bright Data Scraping Implementation (Scrape-Verse)

KisanArbitrage leverages **Bright Data's Web Scraping Infrastructure** to power 100% real-time agricultural intelligence:

1. **MSAMB & Agmarknet Price & Arrival Scraper**
   - Scrapes daily auction bulletins, modal prices, and arrival quantities across Maharashtra & Karnataka APMCs.
   - Bypasses ASP.NET postbacks and dynamic table rendering.
2. **eNAM National Trade Scraper**
   - Scrapes real-time inter-state commodity trade dashboards (`enam.gov.in`), overcoming JavaScript/Angular rendering.
3. **Live District Diesel Scraper**
   - Scrapes daily city/district diesel rates from `mypetrolprice.com` / `goodreturns.in` to ensure logistics calculations reflect real-time fuel inflation.
4. **APMC Statutory Cess & Fee Scraper**
   - Scrapes state marketing board gazettes for exact APMC market cess (e.g., 1.05% in Maharashtra) and loading charges.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Client** | Flutter 3.x (Dart) | Responsive mobile app & web dashboard |
| **Backend** | FastAPI (Python 3.11+) | Asynchronous API gateway & SSE streaming |
| **Agent Orchestrator** | Google Gemini 2.5 Flash | Multi-agent reasoning, intent extraction, synthesis |
| **Arbitrage Engine** | Native Python | Deterministic math, ICAR spoilage, freight formulas |
| **Scraping Engine** | Bright Data Scraping Browser & Web Unlocker | Real-time mandi, eNAM, and fuel data extraction |
| **Language AI** | Bhashini API (with WebSpeech fallback) | Indic ASR, translation, and TTS |
| **Weather API** | Open-Meteo | Hourly route temperature, precipitation, humidity |
| **Routing API** | OpenRouteService | Road distance matrix and transit duration |
| **Notifications** | Twilio WhatsApp Sandbox | Transporter dispatch with human approval gate |
| **Database** | SQLite / Supabase | Pre-seeded with 50+ APMC mandis, historical prices, and community reports |

---

## Project Structure

```
kisanarbitrage/
├── README.md
├── .env.example
├── docs/
│   ├── PRD.md                 # Product Requirements Document
│   ├── ARCHITECTURE.md        # Detailed 4-Tier Architecture & Data Flows
│   ├── TRD.md                 # Technical Requirements & API Specs
│   ├── AGENTS.md              # Multi-Agent Swarm & Engine Specs
│   ├── APP_FLOW.md            # Screen-by-Screen Flow & SSE Events
│   └── UI_UX_DESIGN_BRIEF.md  # Design Tokens & UI Wireframes
├── backend/                   # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # App Entrypoint & CORS
│   │   ├── config.py          # Environment Settings
│   │   ├── agents/            # Gemini Multi-Agent Orchestrator
│   │   ├── scrapers/          # Bright Data Mandi, eNAM & Fuel Scrapers
│   │   ├── services/          # Arbitrage, Logistics, Spoilage & Voice Engines
│   │   ├── routes/            # Sessions, Mandis, Prices, Community, Voice
│   │   ├── db/                # Mandi Master & SQLite/Supabase Models
│   │   └── models/            # Pydantic Schemas
│   ├── tests/                 # Unit & Integration Tests
│   └── requirements.txt
└── app/                       # Flutter Mobile & Web Client
    ├── lib/
    │   ├── main.dart
    │   ├── screens/           # 8 Core Application Screens
    │   ├── widgets/           # Mandi Cards, Sparklines, Badges
    │   ├── services/          # API Client & SSE Stream Listener
    │   └── models/            # Dart Data Models
    └── pubspec.yaml
```

---

## Quick Start

### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Bright Data, Google Gemini, and OpenRouteService keys
```

### 2. Run Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Run Flutter Client (Mobile or Web)
```bash
cd app
flutter pub get
flutter run -d chrome     # Or connect an Android device / emulator
```

---

*Built for Indian farmers. Powered by Bright Data. Built with ❤️*
