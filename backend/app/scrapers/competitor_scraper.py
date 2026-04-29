"""
competitor_scraper.py – Discover competitors and sample their recent activity.

Main export:
  - find_competitors(company_name, category) -> list[dict]
"""

import asyncio
import logging

from bs4 import BeautifulSoup
from googlesearch import search

from .base_scraper import clean_text, fetch_html

logger = logging.getLogger(__name__)

# Domains to skip when extracting competitor names from search results
_SKIP_DOMAINS = {
    "linkedin.com", "facebook.com", "twitter.com", "x.com",
    "wikipedia.org", "youtube.com", "crunchbase.com", "bloomberg.com",
    "reuters.com", "forbes.com", "businessinsider.com", "techcrunch.com",
    "g2.com", "capterra.com", "trustpilot.com",
}


async def find_competitors(
    company_name: str,
    category: str,
    max_competitors: int = 5,
) -> list:
    """
    Return up to *max_competitors* competitors with recent activity snippets.

    Each item:
        {
            "name":            str,
            "website":         str,
            "recent_activity": list[str],   # up to 3 headlines from their news page
        }
    """
    query = f"{company_name} {category} top competitors alternatives"
    seen_names: set[str] = {company_name.lower()}
    competitors: list[dict] = []

    try:
        for url in search(query, num_results=15, sleep_interval=1):
            domain = _extract_domain(url)
            if any(skip in domain for skip in _SKIP_DOMAINS):
                continue

            name = _domain_to_name(domain)
            if name.lower() in seen_names:
                continue

            seen_names.add(name.lower())
            competitors.append(
                {
                    "name": name,
                    "website": f"https://{domain}",
                    "recent_activity": [],
                }
            )

            if len(competitors) >= max_competitors:
                break
    except Exception as exc:  # noqa: BLE001
        logger.error("Google search failed for competitors of '%s': %s", company_name, exc)

    # Enrich each competitor with recent activity (fire concurrently)
    tasks = [_get_competitor_activity(comp["website"]) for comp in competitors]
    activities = await asyncio.gather(*tasks, return_exceptions=True)

    for comp, activity in zip(competitors, activities):
        if isinstance(activity, list):
            comp["recent_activity"] = activity
        else:
            comp["recent_activity"] = []

    logger.info("Found %d competitors for '%s'", len(competitors), company_name)
    return competitors


async def _get_competitor_activity(website: str) -> list:
    """
    Scrape the /news or /press page of a competitor and return up to 3 headlines.
    """
    candidate_paths = ["/news", "/press", "/blog", "/newsroom", "/media"]

    for path in candidate_paths:
        url = website.rstrip("/") + path
        html = await fetch_html(url, timeout=8)
        if not html:
            continue

        soup = BeautifulSoup(html, "lxml")
        # Grab the first few headings that look like article titles
        headings = soup.select("h1, h2, h3")
        headlines = []
        for h in headings:
            text = clean_text(h.get_text())
            if len(text) > 15:  # skip nav items / short labels
                headlines.append(text)
            if len(headlines) >= 3:
                break

        if headlines:
            return headlines

    return []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_domain(url: str) -> str:
    """Return lowercase domain without www. prefix."""
    try:
        domain = url.split("//")[-1].split("/")[0].lower()
        return domain.removeprefix("www.")
    except Exception:
        return url


def _domain_to_name(domain: str) -> str:
    """
    Convert a domain like 'stripe.com' → 'Stripe'.
    Handles hyphens: 'square-up.com' → 'Square Up'.
    """
    base = domain.split(".")[0]
    return base.replace("-", " ").title()
