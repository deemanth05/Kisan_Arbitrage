import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "KisanArbitrage"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    # Gemini AI
    GOOGLE_API_KEY: Optional[str] = None
    
    # Official Government of India Agmarknet Open Data API
    DATA_GOV_IN_API_KEY: str = "579b464db66ec23bdd00000161f10f9e2001428979c3359cf2570ccc"
    
    # Bright Data Scraping (Scrape-Verse)
    BRIGHT_DATA_SCRAPING_BROWSER_URL: Optional[str] = None
    BRIGHT_DATA_WEB_UNLOCKER_URL: Optional[str] = None
    BRIGHT_DATA_API_TOKEN: Optional[str] = None
    BRIGHT_DATA_WEB_UNLOCKER_ZONE: str = "cli_unlocker"
    BRIGHT_DATA_SCRAPING_BROWSER_ZONE: str = "cli_browser"
    
    # OpenRouteService
    OPEN_ROUTE_API_KEY: Optional[str] = None
    
    # Bhashini Indic Services
    BHASHINI_API_KEY: Optional[str] = None
    BHASHINI_USER_ID: Optional[str] = None
    BHASHINI_PIPELINE_ID: Optional[str] = None
    
    # Twilio WhatsApp
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./kisan_arbitrage.db"
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
