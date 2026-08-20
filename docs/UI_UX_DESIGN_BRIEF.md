# KisanArbitrage: UI/UX Design Brief

## 1. Overview
KisanArbitrage is an autonomous mandi price arbitrage & freight optimization agent for Indian farmers. The application, built with **Flutter 3.x (Dart)**, supports both **Mobile (Android/iOS)** and **Web (Browser)**. The primary goal is to provide a highly accessible, localized, and actionable interface for farmers to make data-driven selling decisions with full financial clarity.

---

## 2. Design Principles
- **Accessibility & Voice-First**: Designed for diverse literacy levels, heavily relying on voice input, text-to-speech (TTS), iconography, and high-contrast visual cues.
- **Data-Driven Action**: It is NOT just a price lookup app. It is an agentic net-arbitrage engine. The UI highlights the *recommendation* and the *net gain math* (revenue minus freight, cess, and spoilage).
- **Trust & Transparency**: Build trust through verified scraped sources (MSAMB, eNAM, Live Diesel), benchmark trust badges, and expandable agent reasoning.
- **Vernacular Localization**: Full native Indic language support (Hindi, Marathi, English) powered by Bhashini AI with Web Speech API fallback.

---

## 3. Global Styling & Tokens

### Typography
- **Primary (Headings & Financial Numbers)**: Poppins (Bold / SemiBold)
- **Secondary (Body & UI Labels)**: Noto Sans (supports Devanagari script natively)
- **Agent Logs & Scraper Reasoning**: JetBrains Mono (monospaced)

### Color Palette
- **Primary Green**: `#2E7D32` (Action buttons, positive net arbitrage, high contrast)
- **Success Light**: `#E8F5E9` (Background for recommended cards and positive badges)
- **Success Dark**: `#1B5E20` (Text for positive metrics)
- **Warning Amber/Orange**: `#F57C00` (Moderate risk, heat alerts)
- **Warning Light**: `#FFF3E0`
- **Warning Dark**: `#E65100`
- **Danger Red**: `#C62828` (Negative arbitrage, below benchmark, severe spoilage)
- **Danger Light**: `#FFEBEE`
- **Neutral Gray**: `#F5F5F5` (Card backgrounds, dividers)
- **Text Primary**: `#212121`
- **Text Secondary**: `#616161`
- **Gradient Accent**: `#E3F2FD` to `#BBDEFB` (Predictive banner)

---

## 4. Key Component Specifications

### 4.1 Voice Input Component (Bhashini & WebSpeech)
- **Description**: Large floating action button for voice queries.
- **Specs**:
  - Size: 64dp FAB.
  - Default: Primary Green (`#2E7D32`) with white microphone icon.
  - Recording State: Pulses Red (`#C62828`) with real-time waveform animation.
  - Transcribed Text: Live bottom sheet overlay showing recognized Indic text.
  - Auto-fill: Auto-populates crop, quantity, and origin city.

### 4.2 Benchmark Trust Badge (MSP & TOP Operation Greens)
- **Description**: Pill badge indicating price relative to government benchmark.
- **States**:
  - **Above Benchmark**: Background `#E8F5E9`, Text `✅ ₹400 ABOVE BENCHMARK`, Color `#1B5E20`.
  - **At Benchmark**: Background `#FFF3E0`, Text `➡️ AT BENCHMARK`, Color `#E65100`.
  - **Below Benchmark**: Background `#FFEBEE`, Text `⚠️ ₹200 BELOW BENCHMARK`, Color `#C62828`.

### 4.3 7-Day Sparkline Chart
- **Description**: Miniature historical trend line rendered via `fl_chart`.
- **Specs**:
  - Height: 40dp.
  - Green (Upward trend), Red (Downward), Gray (Flat).
  - Subtle 20% opacity fill gradient underneath the line.

### 4.4 Market Pulse (Arrival Intelligence)
- **States**:
  - **High Arrivals (Scarcity Warning / High Demand)**: `📦 High Arrivals` (Color: `#1B5E20` or `#C62828` depending on price momentum).
  - **Normal Arrivals**: `📦 Normal Supply` (Color: `#616161`).

### 4.5 Community Ground-Truth Badge
- **Description**: Shows crowdsourced price reported by peer farmers.
- **Specs**: `👥 Farmers report: ₹2,050/q (3h ago)` displayed below official price.

### 4.6 TTS Audio Playback Button
- **Description**: Speaker icon `🔊` in the app bar to play audio summary in the farmer's selected language.

### 4.7 Hero Mandi Profit Card
- **Layout**:
  - Header: Mandi Name + Distance (km).
  - Top-Right: `🏆 RECOMMENDED` ribbon on top choice.
  - Hero Metric: Net Profit (Large Poppins 22sp, `#1B5E20`).
  - Row 1: Benchmark Badge (`✅ ₹400 ABOVE BENCHMARK`).
  - Row 2: 7-Day Sparkline Chart + Market Pulse Badge.
  - Expandable Breakdown:
    - Expected Gross Value: `+₹42,000`
    - Real Freight (Live Diesel): `-₹2,100`
    - APMC Statutory Cess & Loading: `-₹800`
    - ICAR Spoilage Loss (Route Heat Alert): `-₹600 (3%)`
  - Action CTA: "Select this Mandi" button.

### 4.8 Expandable Agent Reasoning Panel
- **Description**: Accordion revealing live subagent reasoning and scraper tool executions.
- **Specs**: Monospaced font, displaying MSAMB, eNAM, live diesel, and Open-Meteo execution logs.

---

## 5. Screen Layout Specifications

### Screen 1: Onboarding
- KisanArbitrage Logo + Hero Illustration.
- "नमस्ते! भाषा चुनें / Choose Language".
- 3 Language Selection Cards (🇮🇳 हिंदी | 🇮🇳 मराठी | 🇬🇧 English).
- CTA: "Get Started →".

### Screen 2: Home & Query
- Header: User greeting + weather badge.
- Main Query Card:
  - Commodity Dropdown (Tomato, Onion, Potato, Soybean, Cotton, Wheat, Green Chilli).
  - Quantity & Unit row (20 Quintals).
  - Location input with "Use GPS" button.
  - Vehicle Type selector (Bolero Pickup, Tata Ace, Eicher 14ft).
  - CTA: "Find Best Mandi" (Green 56dp button).
- Floating Mic Button: Prominent in bottom right.
- Market Pulse Feed: 3 horizontal cards showing trending crops.
- Community Ground-Truth Feed: Recent reports.

### Screen 3: Processing & Live Agent Swarm
- Scanning radar animation.
- 4 Subagent Status Tiles:
  1. 🔍 **Market Intel**: Scraping MSAMB & eNAM prices via Bright Data...
  2. 🚚 **Logistics Intel**: Scraping live diesel rates & computing route matrix...
  3. 🌤️ **Weather Risk**: Querying Open-Meteo for heat & rainfall spoilage...
  4. 📜 **Scheme Intel**: Evaluating PM-KISAN & PMFBY eligibility...
- Live progress indicator transitioning to "Computing net arbitrage in Python engine...".

### Screen 4: Profit Comparison (Hero Screen)
- App Bar with TTS Voice Button (`🔊`).
- Query Summary Chip: `🍅 Tomato • 20 Quintals • From Kolhapur`.
- "Best Time to Sell" Predictive Banner (`🔮 SELL TODAY: Severe heat along route`).
- Vertical stack of Mandi Profit Cards (Top choice highlighted with `#E8F5E9` background and `BEST` ribbon).
- Sticky Bottom Bar: "Sell Locally" vs "Select Recommended Mandi →".

### Screen 5: Government Schemes Carousel
- Swipeable cards for PM-KISAN, PMFBY (Crop Insurance), and eNAM Direct Marketing.
- Eligibility status with direct enrollment link.
- CTA: "Continue to Dispatch →".

### Screen 6: Transporter Approval Gate
- Bottom sheet modal displaying comparison: Local Mandi vs Target Mandi.
- Transparent net savings calculation: `You make ₹4,500 MORE by selling at Pune`.
- Transporter pickup details: Bolero Pickup, Kolhapur pickup ETA ~2 hours.
- Warning: `⚠️ Transporter will be alerted via WhatsApp with pickup order`.
- Action: `✅ Approve & Notify Transporter` (Swipes or taps to confirm).

### Screen 7: Confirmation & Success
- Confetti animation and green checkmark.
- "Transporter Notified via WhatsApp!"
- Pickup summary and link back to Home.

### Screen 8 & 9: History & Community Price Feed
- Filterable past transactions and crowdsourced ground-truth price reporting modal.

---

## 6. Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| **Mobile Phone** | <600dp | Single column stacked layout, bottom navigation |
| **Tablet / Web** | 600dp - 1024dp | 2-column layout: Query/Inputs on left, Live Results on right |
| **Desktop Web** | >1024dp | Centered max-width 1200dp layout with side-by-side cost breakdown |

---

## 7. Loading, Empty & Error States

- **Loading Animation**: Scanning radar with real-time subagent status transitions.
- **Partial Data Gracefulness**: Yellow banner if a live secondary source is unavailable, falling back to cached averages.
- **Voice Failure Fallback**: Instant fallback to manual form and Web Speech API.
- **Timeout**: Graceful retry CTA without crashing.
