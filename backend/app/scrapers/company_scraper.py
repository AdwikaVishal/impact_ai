"""
company_scraper.py – Find a company's website and extract about-page content.

Main exports:
  - get_company_website(company_name, category) -> str
  - scrape_about_page(website)                  -> dict
"""

import asyncio
import logging
import re
from typing import Optional

from bs4 import BeautifulSoup
from googlesearch import search

from .base_scraper import clean_text, fetch_html

logger = logging.getLogger(__name__)

# Domains that are NOT the company's own website
_BLOCKED_DOMAINS = {
    "linkedin.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "wikipedia.org",
    "instagram.com",
    "youtube.com",
    "crunchbase.com",
    "bloomberg.com",
    "reuters.com",
    "glassdoor.com",
    "indeed.com",
    "yelp.com",
}


async def get_company_website(company_name: str, category: str = "") -> str:
    """
    Search Google for the company's official website.

    Args:
        company_name: Human-readable company name (e.g. "Stripe").
        category:     Industry/category hint (e.g. "online payment processing").

    Returns:
        Root URL string (e.g. "https://stripe.com") or empty string if not found.
    """
    query = f"{company_name} official website"
    if category:
        query = f"{company_name} {category} official website"

    try:
        for url in search(query, num_results=5, sleep_interval=1):
            domain = _extract_domain(url)
            if not any(blocked in domain for blocked in _BLOCKED_DOMAINS):
                # Return just the root (scheme + domain)
                root = _root_url(url)
                logger.info("Found website for %s: %s", company_name, root)
                return root
    except Exception as exc:  # noqa: BLE001
        logger.error("Google search failed for '%s': %s", company_name, exc)

    return ""


async def scrape_about_page(website: str) -> dict:
    """
    Try common about-page paths and extract text + scale indicators.

    Args:
        website: Root URL (e.g. "https://stripe.com").

    Returns:
        {
            "about_text":  str   – up to 5 000 chars of page text,
            "revenue":     str | None,
            "employees":   str | None,
        }
    """
    candidate_paths = ["/about", "/about-us", "/company", "/who-we-are", "/our-story"]

    for path in candidate_paths:
        url = website.rstrip("/") + path
        html = await fetch_html(url)
        if not html:
            await asyncio.sleep(0.5)
            continue

        soup = BeautifulSoup(html, "lxml")

        # Prefer semantic containers; fall back to <body>
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("section")
            or soup.body
        )
        raw_text = main_content.get_text(separator=" ") if main_content else ""
        text = clean_text(raw_text)

        # Extract scale indicators via regex
        revenue_match = re.search(
            r"\$\s*\d+(?:\.\d+)?\s*(?:billion|million|B|M)\b", text, re.I
        )
        employees_match = re.search(
            r"(\d{1,3}(?:,\d{3})*)\s*(?:\+\s*)?(?:employees|people|team members|staff)\b",
            text,
            re.I,
        )
        founded_match = re.search(r"(?:founded|established)\s+(?:in\s+)?(\d{4})", text, re.I)

        result = {
            "about_text": text[:5000],
            "revenue": revenue_match.group(0).strip() if revenue_match else None,
            "employees": employees_match.group(1) if employees_match else None,
            "founded": founded_match.group(1) if founded_match else None,
        }
        logger.info("Scraped about page for %s: %s", website, path)
        return result

    logger.warning("No about page found for %s", website)
    return {"about_text": "", "revenue": None, "employees": None, "founded": None}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_domain(url: str) -> str:
    """Return the domain portion of a URL (lowercase, no www.)."""
    try:
        domain = url.split("//")[-1].split("/")[0].lower()
        return domain.removeprefix("www.")
    except Exception:
        return url


def _root_url(url: str) -> str:
    """Return scheme + domain only (strip path/query/fragment)."""
    try:
        parts = url.split("//")
        scheme = parts[0]  # e.g. "https:"
        rest = parts[1].split("/")[0]  # domain only
        return f"{scheme}//{rest}"
    except Exception:
        return url
