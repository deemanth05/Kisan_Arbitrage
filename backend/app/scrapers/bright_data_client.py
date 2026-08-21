import httpx
import logging
import asyncio
import subprocess
import shutil
import json
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
    Client for interacting with Bright Data Web Unlocker, Scraping Browser, and CLI.
    
    Priority Order:
    1. HTTP Proxy URL if configured (BRIGHT_DATA_WEB_UNLOCKER_URL).
    2. Bright Data CLI (`bdata scrape`) using the active authenticated session.
    3. Direct HTTPS request with anti-bot headers.
    """
    def __init__(self):
        self.proxy_url = settings.BRIGHT_DATA_WEB_UNLOCKER_URL
        self.api_token = settings.BRIGHT_DATA_API_TOKEN
        self.scraping_browser_url = settings.BRIGHT_DATA_SCRAPING_BROWSER_URL
        
    async def fetch_via_cli(self, url: str) -> Optional[str]:
        """
        Executes bdata scrape via authenticated CLI session.
        """
        try:
            npx_cmd = shutil.which("npx") or "npx"
            process = await asyncio.create_subprocess_exec(
                npx_cmd, "-p", "@brightdata/cli", "bdata", "scrape", url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=35.0)
            if process.returncode == 0 and stdout:
                content = stdout.decode("utf-8", errors="replace")
                logger.info(f"Successfully scraped {url} via Bright Data CLI ({len(content)} bytes)")
                return content
            else:
                err_msg = stderr.decode("utf-8", errors="replace")
                logger.warning(f"bdata scrape CLI returned code {process.returncode}: {err_msg[:150]}")
        except Exception as e:
            logger.warning(f"bdata scrape CLI execution error: {e}")
        return None

    async def fetch_html(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 25.0,
        use_bright_data: bool = True
    ) -> str:
        req_headers = {**DEFAULT_HEADERS, **(headers or {})}
        
        # 1. Use Proxy URL if configured
        if use_bright_data and self.proxy_url:
            try:
                logger.info(f"Scraping {url} via Bright Data proxy URL...")
                async with httpx.AsyncClient(
                    proxy=self.proxy_url,
                    headers=req_headers,
                    timeout=timeout,
                    follow_redirects=True,
                    verify=False
                ) as client:
                    resp = await client.get(url, params=params)
                    resp.raise_for_status()
                    return resp.text
            except Exception as e:
                logger.warning(f"Bright Data proxy URL error: {e}. Falling back to CLI/Direct.")

        # 2. Use Authenticated Bright Data CLI
        if use_bright_data and not params:
            cli_result = await self.fetch_via_cli(url)
            if cli_result and len(cli_result) > 50:
                return cli_result

        # 3. Direct request with custom headers
        async with httpx.AsyncClient(
            headers=req_headers,
            timeout=timeout,
            follow_redirects=True
        ) as client:
            logger.info(f"Fetching {url} directly...")
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.text

    async def post_data(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 25.0,
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
            if json_body is not None:
                response = await client.post(url, json=json_body)
            else:
                response = await client.post(url, data=data)
            response.raise_for_status()
            return response.text

bright_data_client = BrightDataClient()
