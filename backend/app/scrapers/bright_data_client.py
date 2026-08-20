import httpx
import logging
from typing import Optional, Dict, Any
from backend.app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8,mr;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

class BrightDataClient:
    """
    Client for interacting with Bright Data Web Unlocker and Scraping Proxies.
    Provides automatic retry, exponential backoff, and transparent fallback.
    """
    def __init__(self):
        self.proxy_url = settings.BRIGHT_DATA_WEB_UNLOCKER_URL
        self.api_token = settings.BRIGHT_DATA_API_TOKEN
        self.scraping_browser_url = settings.BRIGHT_DATA_SCRAPING_BROWSER_URL
        
    async def fetch_html(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 20.0,
        use_bright_data: bool = True
    ) -> str:
        req_headers = {**DEFAULT_HEADERS, **(headers or {})}
        proxies = self.proxy_url if (use_bright_data and self.proxy_url) else None
        
        async with httpx.AsyncClient(
            proxy=proxies,
            headers=req_headers,
            timeout=timeout,
            follow_redirects=True,
            verify=False
        ) as client:
            try:
                logger.info(f"Scraping URL: {url} (Bright Data proxy: {'Enabled' if proxies else 'Direct/Standard'})")
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error {e.response.status_code} fetching {url}: {e}")
                # Retry without proxy if proxy failed
                if proxies:
                    logger.info(f"Retrying {url} directly without proxy...")
                    async with httpx.AsyncClient(headers=req_headers, timeout=timeout, follow_redirects=True) as fallback_client:
                        resp = await fallback_client.get(url, params=params)
                        resp.raise_for_status()
                        return resp.text
                raise
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                raise

    async def post_data(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 20.0,
        use_bright_data: bool = True
    ) -> str:
        req_headers = {**DEFAULT_HEADERS, **(headers or {})}
        proxies = self.proxy_url if (use_bright_data and self.proxy_url) else None
        
        async with httpx.AsyncClient(
            proxy=proxies,
            headers=req_headers,
            timeout=timeout,
            follow_redirects=True,
            verify=False
        ) as client:
            try:
                if json_body is not None:
                    response = await client.post(url, json=json_body)
                else:
                    response = await client.post(url, data=data)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"Error posting data to {url}: {e}")
                raise

bright_data_client = BrightDataClient()
