"""
competitor_scraper.py – Discover competitors and sample their recent activity.

Source priority:
  1. Wikipedia  – structured "competitors / see also" links (free, reliable)
  2. Serper     – Google Search API (set SERPER_KEY in .env; 2 500 free req/mo)
  3. googlesearch-python – direct Google scrape fallback (no key needed)

Main export:
  - find_competitors(company_name, category) -> list[dict]
"""

import asyncio
import logging
import os

import aiohttp
import wikipedia
from bs4 import BeautifulSoup
from googlesearch import search

from .base import clean_text, fetch_html

logger = logging.getLogger(__name__)

_SERPER_URL = "https://google.serper.dev/search"

# Domains that are NOT a company's own website
_SKIP_DOMAINS = {
    "linkedin.com", "facebook.com", "twitter.com", "x.com",
    "wikipedia.org", "youtube.com", "crunchbase.com", "bloomberg.com",
    "reuters.com", "forbes.com", "businessinsider.com", "techcrunch.com",
    "g2.com", "capterra.com", "trustpilot.com", "glassdoor.com",
}

# Wikipedia category keywords that suggest a company article
_COMPANY_LINK_KEYWORDS = {
    "company", "corporation", "inc", "ltd", "llc", "group",
    "technologies", "software", "services", "solutions", "systems",
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
            "source":          str,   # "Wikipedia" | "Serper" | "Google"
            "recent_activity": list[str],
        }
    """
    seen_names: set[str] = {company_name.lower()}
    competitors: list[dict] = []

    # ── 1. Wikipedia ────────────────────────────────────────────────────────
    wiki_competitors = await _competitors_from_wikipedia(company_name, category)
    for c in wiki_competitors:
        if c["name"].lower() not in seen_names and len(competitors) < max_competitors:
            seen_names.add(c["name"].lower())
            competitors.append(c)

    # ── 2. Serper (if key present and we still need more) ───────────────────
    serper_key: str | None = os.getenv("SERPER_KEY")
    if serper_key and len(competitors) < max_competitors:
        serper_competitors = await _competitors_from_serper(
            company_name, category, serper_key, max_competitors - len(competitors)
        )
        for c in serper_competitors:
            if c["name"].lower() not in seen_names and len(competitors) < max_competitors:
                seen_names.add(c["name"].lower())
                competitors.append(c)

    # ── 3. googlesearch fallback ─────────────────────────────────────────────
    if len(competitors) < max_competitors:
        google_competitors = await _competitors_from_google(
            company_name, category, seen_names, max_competitors - len(competitors)
        )
        competitors.extend(google_competitors)

    # ── Enrich with recent activity (concurrent) ────────────────────────────
    tasks = [_get_competitor_activity(c["website"]) for c in competitors]
    activities = await asyncio.gather(*tasks, return_exceptions=True)
    for comp, activity in zip(competitors, activities):
        comp["recent_activity"] = activity if isinstance(activity, list) else []

    logger.info(
        "[competitors] Found %d for '%s' (wiki=%d, serper=%d, google=%d)",
        len(competitors), company_name,
        sum(1 for c in competitors if c.get("source") == "Wikipedia"),
        sum(1 for c in competitors if c.get("source") == "Serper"),
        sum(1 for c in competitors if c.get("source") == "Google"),
    )
    return competitors[:max_competitors]


# ---------------------------------------------------------------------------
# Source 1 – Wikipedia
# ---------------------------------------------------------------------------

async def _competitors_from_wikipedia(company_name: str, category: str) -> list:
    """
    Pull competitor names from the Wikipedia page for the company or its industry.

    Strategy:
      a) Try the company page directly – look for "Competitors" section or
         links whose anchor text contains company-like keywords.
      b) Try "List of {category} companies" page.
    """
    def _sync() -> list:
        results = []
        # a) Company page
        try:
            page = wikipedia.page(company_name, auto_suggest=True)
            for link in page.links:
                lower = link.lower()
                if any(kw in lower for kw in _COMPANY_LINK_KEYWORDS):
                    if link.lower() != company_name.lower():
                        results.append({
                            "name":   link,
                            "website": f"https://www.{link.lower().replace(' ', '')}.com",
                            "source": "Wikipedia",
                        })
                if len(results) >= 10:
                    break
        except Exception as exc:
            logger.debug("[competitors] Wikipedia company page failed for '%s': %s", company_name, exc)

        # b) Industry list page
        if len(results) < 3 and category:
            try:
                list_page = wikipedia.page(f"List of {category} companies", auto_suggest=True)
                for link in list_page.links:
                    lower = link.lower()
                    if any(kw in lower for kw in _COMPANY_LINK_KEYWORDS):
                        if link.lower() != company_name.lower():
                            results.append({
                                "name":    link,
                                "website": f"https://www.{link.lower().replace(' ', '')}.com",
                                "source":  "Wikipedia",
                            })
                    if len(results) >= 10:
                        break
            except Exception as exc:
                logger.debug("[competitors] Wikipedia list page failed for '%s': %s", category, exc)

        return results

    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(None, _sync)
    except Exception as exc:  # noqa: BLE001
        logger.warning("[competitors] Wikipedia executor failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Source 2 – Serper
# ---------------------------------------------------------------------------

async def _competitors_from_serper(
    company_name: str,
    category: str,
    api_key: str,
    limit: int,
) -> list:
    query = f"{company_name} {category} top competitors alternatives"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                _SERPER_URL,
                json={"q": query, "num": 10},
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    logger.warning("[competitors] Serper HTTP %s", resp.status)
                    return []
                data = await resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("[competitors] Serper request failed: %s", exc)
        return []

    results = []
    for item in data.get("organic", []):
        link: str = item.get("link", "")
        domain = _extract_domain(link)
        if any(skip in domain for skip in _SKIP_DOMAINS):
            continue
        name = _domain_to_name(domain)
        results.append({
            "name":    name,
            "website": f"https://{domain}",
            "source":  "Serper",
        })
        if len(results) >= limit:
            break

    return results


# ---------------------------------------------------------------------------
# Source 3 – googlesearch fallback
# ---------------------------------------------------------------------------

async def _competitors_from_google(
    company_name: str,
    category: str,
    seen_names: set,
    limit: int,
) -> list:
    query = f"{company_name} {category} top competitors alternatives"
    results = []
    try:
        for url in search(query, num_results=15, sleep_interval=1):
            domain = _extract_domain(url)
            if any(skip in domain for skip in _SKIP_DOMAINS):
                continue
            name = _domain_to_name(domain)
            if name.lower() in seen_names:
                continue
            seen_names.add(name.lower())
            results.append({
                "name":    name,
                "website": f"https://{domain}",
                "source":  "Google",
            })
            if len(results) >= limit:
                break
    except Exception as exc:  # noqa: BLE001
        logger.error("[competitors] googlesearch failed: %s", exc)
    return results


# ---------------------------------------------------------------------------
# Activity enrichment
# ---------------------------------------------------------------------------

async def _get_competitor_activity(website: str) -> list:
    """Scrape /news or /blog and return up to 3 headline strings."""
    for path in ["/news", "/press", "/blog", "/newsroom", "/media"]:
        html = await fetch_html(website.rstrip("/") + path, timeout=8)
        if not html:
            continue
        soup = BeautifulSoup(html, "lxml")
        headlines = []
        for h in soup.select("h1, h2, h3"):
            text = clean_text(h.get_text())
            if len(text) > 15:
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
    try:
        domain = url.split("//")[-1].split("/")[0].lower()
        return domain.removeprefix("www.")
    except Exception:
        return url


def _domain_to_name(domain: str) -> str:
    base = domain.split(".")[0]
    return base.replace("-", " ").title()
