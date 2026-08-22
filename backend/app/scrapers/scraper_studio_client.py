import json
import shutil
import asyncio
import logging
from typing import List, Dict, Any, Optional
from backend.app.config import settings

logger = logging.getLogger(__name__)

class ScraperStudioClient:
    """
    Client for triggering Bright Data Scraper Studio custom collectors and SERP searches
    via the authenticated Bright Data CLI (`bdata`).
    """
    
    def __init__(self):
        self.diesel_collector_id = settings.COLLECTOR_DIESEL_PRICES
        self.api_token = settings.BRIGHT_DATA_API_TOKEN
        
    async def trigger_collector(self, collector_id: str, url: str, timeout: float = 40.0) -> List[Dict[str, Any]]:
        """
        Runs `bdata scraper run <collector_id> <url> --pretty`
        """
        if not collector_id:
            logger.warning("No collector_id provided to trigger_collector.")
            return []
            
        try:
            npx_cmd = shutil.which("npx") or "npx"
            cmd = [npx_cmd, "-p", "@brightdata/cli", "bdata", "scraper", "run", collector_id, url, "--pretty"]
            logger.info(f"Triggering Scraper Studio collector {collector_id} for URL: {url}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            
            if process.returncode == 0 and stdout:
                data = json.loads(stdout.decode("utf-8"))
                if isinstance(data, list):
                    logger.info(f"Collector {collector_id} returned {len(data)} records.")
                    return data
            else:
                err_msg = stderr.decode("utf-8", errors="replace")
                logger.warning(f"Collector {collector_id} execution returned code {process.returncode}: {err_msg[:200]}")
        except Exception as e:
            logger.error(f"Error executing Scraper Studio collector {collector_id}: {e}")
            
        return []

    async def search_serp(self, query: str, timeout: float = 20.0) -> List[Dict[str, Any]]:
        """
        Runs `bdata search "<query>"` using Bright Data SERP API.
        """
        results = []
        try:
            npx_cmd = shutil.which("npx") or "npx"
            cmd = [npx_cmd, "-p", "@brightdata/cli", "bdata", "search", query]
            logger.info(f"Executing Bright Data SERP search: {query}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            
            if process.returncode == 0 and stdout:
                lines = stdout.decode("utf-8").strip().split("\n")
                # Parse table lines (header line, separator, data rows)
                for line in lines[2:]:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 4 and parts[0].isdigit():
                        results.append({
                            "rank": int(parts[0]),
                            "title": parts[1],
                            "url": parts[2],
                            "description": parts[3]
                        })
        except Exception as e:
            logger.warning(f"Error executing Bright Data SERP search: {e}")
            
        return results

scraper_studio_client = ScraperStudioClient()
