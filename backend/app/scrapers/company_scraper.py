"""
company_scraper.py – Find a company's website and extract about-page content.

Main exports:
  - get_company_website(company_name, category) -> str  (delegates to base.find_website)
  - scrape_about_page(website)                  -> dict
"""

import asyncio
import logging
import re

from bs4 import BeautifulSoup

from .base import clean_text, fetch_html, find_website

logger = logging.getLogger(__name__)


async def get_company_website(company_name: str, category: str = "") -> str:
    """Alias for base.find_website – kept for backward compatibility."""
    return await find_website(company_name, category)


async def scrape_about_page(website: str) -> dict:
    """
    Try common about-page paths and extract text + scale indicators.

    Returns:
        {
            "about_text":  str   – up to 5 000 chars of page text,
            "revenue":     str | None,
            "employees":   str | None,
            "founded":     str | None,
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
