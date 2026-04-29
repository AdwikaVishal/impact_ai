"""
base.py – Shared scraping utilities (fetch, domain helpers, website discovery).

This is the single import point for low-level helpers used by all scrapers.
"""

import asyncio
import logging
import re
from typing import Optional

import aiohttp
import tldextract
from bs4 import BeautifulSoup
from googlesearch import search

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

_ua_index = 0

_SOCIAL_DOMAINS = {
    "linkedin.com", "facebook.com", "twitter.com", "x.com",
    "instagram.com", "youtube.com", "wikipedia.org", "crunchbase.com",
    "bloomberg.com", "reuters.com", "glassdoor.com", "indeed.com",
}


def _next_ua() -> str:
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
    Async HTTP GET with retry and user-agent rotation.
    Returns HTML string on success, None on failure.
    """
    headers = {
        "User-Agent": _next_ua(),
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


def extract_domain(url: str) -> str:
    """
    Return 'domain.tld' using tldextract (handles ccTLDs correctly).
    e.g. 'https://www.stripe.com/about' → 'stripe.com'
    """
    ext = tldextract.extract(url)
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}"
    # fallback: strip scheme + www + path
    try:
        raw = url.split("//")[-1].split("/")[0].lower()
        return raw.removeprefix("www.")
    except Exception:
        return url


def clean_text(text: str) -> str:
    """Collapse whitespace."""
    return re.sub(r"\s+", " ", text).strip()


def extract_text(soup: BeautifulSoup, selector: str) -> str:
    """Return stripped text of first CSS-selector match, or ''."""
    elem = soup.select_one(selector)
    return elem.get_text(strip=True) if elem else ""


async def find_website(company_name: str, category: str = "") -> str:
    """
    Google-search for the company's official website.
    Returns root URL (e.g. 'https://stripe.com') or '' if not found.
    """
    # First try known website patterns (no Google search)
    known_websites = {
        "stripe": "https://stripe.com",
        "nike": "https://nike.com",
        "spotify": "https://spotify.com",
        "apple": "https://apple.com",
        "google": "https://google.com",
        "microsoft": "https://microsoft.com",
        "amazon": "https://amazon.com",
        "netflix": "https://netflix.com",
        "tesla": "https://tesla.com",
        "shopify": "https://shopify.com",
    }
    
    company_lower = company_name.lower()
    if company_lower in known_websites:
        url = known_websites[company_lower]
        logger.info("Found website for '%s' from known list: %s", company_name, url)
        return url
    
    # Try common patterns directly (skip Google)
    common_patterns = [
        f"https://www.{company_lower}.com",
        f"https://{company_lower}.com",
        f"https://www.{company_lower}.io",
        f"https://{company_lower}.io",
        f"https://www.{company_lower}.co",
        f"https://{company_lower}.co",
    ]
    
    for url in common_patterns:
        html = await fetch_html(url, timeout=5)
        if html:
            logger.info("Found website for '%s' by pattern: %s", company_name, url)
            return url
    
    # Fallback to Google search
    query = f"{company_name} official website"
    if category:
        query = f"{company_name} {category} official website"

    try:
        for url in search(query, num_results=5, sleep_interval=2):
            domain = extract_domain(url)
            if not any(bad in domain for bad in _SOCIAL_DOMAINS):
                parts = url.split("//")
                root = f"{parts[0]}//{parts[1].split('/')[0]}"
                logger.info("Found website for '%s' via Google: %s", company_name, root)
                return root
    except Exception as exc:
        logger.error("find_website Google search failed for '%s': %s", company_name, exc)
    
    # Last resort: construct from name
    fallback_url = f"https://www.{company_lower}.com"
    logger.warning("No website found for '%s', using fallback: %s", company_name, fallback_url)
    return fallback_url