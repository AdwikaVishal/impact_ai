"""
base_scraper.py – Shared utilities for all scrapers.

Provides:
  - fetch_html()   : async HTTP GET with retry and user-agent rotation
  - extract_text() : CSS-selector helper
  - clean_text()   : whitespace normaliser
"""

import asyncio
import logging
import re
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Rotate user-agents to reduce bot-detection blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

_ua_index = 0


def _next_user_agent() -> str:
    """Round-robin through the user-agent list."""
    global _ua_index
    ua = USER_AGENTS[_ua_index % len(USER_AGENTS)]
    _ua_index += 1
    return ua


async def fetch_html(
    url: str,
    timeout: int = 12,
    retries: int = 2,
    delay: float = 1.0,
) -> Optional[str]:
    """
    Async HTTP GET that returns the response body as a string.

    Args:
        url:     Target URL.
        timeout: Per-request timeout in seconds.
        retries: Number of retry attempts on failure.
        delay:   Seconds to wait between retries.

    Returns:
        HTML string on success, None on failure.
    """
    headers = {
        "User-Agent": _next_user_agent(),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    for attempt in range(retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    allow_redirects=True,
                ) as resp:
                    if resp.status == 200:
                        return await resp.text(errors="replace")
                    logger.warning("HTTP %s for %s", resp.status, url)
        except asyncio.TimeoutError:
            logger.warning("Timeout fetching %s (attempt %d)", url, attempt + 1)
        except aiohttp.ClientError as exc:
            logger.warning("Client error fetching %s: %s", url, exc)
        except Exception as exc:  # noqa: BLE001
            logger.error("Unexpected error fetching %s: %s", url, exc)

        if attempt < retries:
            await asyncio.sleep(delay)

    return None


def extract_text(soup: BeautifulSoup, selector: str) -> str:
    """
    Return the stripped text of the first element matching *selector*.

    Returns an empty string if nothing is found.
    """
    elem = soup.select_one(selector)
    return elem.get_text(strip=True) if elem else ""


def clean_text(text: str) -> str:
    """Collapse whitespace and strip leading/trailing spaces."""
    return re.sub(r"\s+", " ", text).strip()
