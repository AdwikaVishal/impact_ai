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
    Also tries homepage if about pages fail.
    """
    if not website:
        return {"about_text": "", "revenue": None, "employees": None, "founded": None}
    
    candidate_paths = ["/about", "/about-us", "/company", "/who-we-are", "/our-story"]
    
    # Try about pages first
    for path in candidate_paths:
        url = website.rstrip("/") + path
        html = await fetch_html(url, timeout=8)
        if not html:
            continue
        
        result = await _extract_from_html(html, website, path)
        if result and result.get("about_text") and len(result["about_text"]) > 100:
            logger.info("Scraped about page for %s: %s", website, path)
            return result
        
        await asyncio.sleep(0.5)
    
    # If no about page, try homepage
    logger.info("No about page found, trying homepage for %s", website)
    html = await fetch_html(website, timeout=8)
    if html:
        result = await _extract_from_html(html, website, "/")
        if result:
            return result
    
    logger.warning("No content found for %s", website)
    return {"about_text": "", "revenue": None, "employees": None, "founded": None}


async def _extract_from_html(html: str, website: str, path: str) -> dict:
    """Extract text and indicators from HTML."""
    soup = BeautifulSoup(html, "lxml")
    
    # Try to find main content area
    main_content = (
        soup.find("main") or
        soup.find("article") or
        soup.find("section", class_=re.compile(r"about|content|hero")) or
        soup.find("div", class_=re.compile(r"about|content|description")) or
        soup.body
    )
    
    if not main_content:
        return None
    
    raw_text = main_content.get_text(separator=" ")
    text = clean_text(raw_text)
    
    if not text or len(text) < 50:
        return None
    
    # Extract scale indicators
    revenue_match = re.search(
        r"\$\s*\d+(?:\.\d+)?\s*(?:billion|million|B|M)\b", text, re.I
    )
    employees_match = re.search(
        r"(\d{1,3}(?:,\d{3})*)\s*(?:\+\s*)?(?:employees|people|team members|staff)\b",
        text, re.I
    )
    founded_match = re.search(r"(?:founded|established)\s+(?:in\s+)?(\d{4})", text, re.I)
    
    return {
        "about_text": text[:5000],
        "revenue": revenue_match.group(0).strip() if revenue_match else None,
        "employees": employees_match.group(1) if employees_match else None,
        "founded": founded_match.group(1) if founded_match else None,
    }