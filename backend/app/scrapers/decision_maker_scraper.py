"""
decision_maker_scraper.py – Find marketing/brand decision-makers at a company.

Source priority:
  1. Hunter.io domain-search API  (set HUNTER_API_KEY in .env)
  2. Serper LinkedIn search        (set SERPER_KEY in .env – better than raw Google)
  3. googlesearch-python fallback  (no key needed)

Main export:
  - find_decision_makers(company_name, domain) -> list[dict]
"""

import asyncio
import logging
import os
from typing import Optional

import aiohttp
from googlesearch import search

from .serper_helper import serper_search

logger = logging.getLogger(__name__)

_TARGET_ROLES = [
    "CMO",
    "Chief Marketing Officer",
    "VP of Marketing",
    "VP Marketing",
    "Head of Marketing",
    "Brand Manager",
    "Head of Brand",
    "Director of Marketing",
    "Head of Communications",
    "Communications Director",
    "CEO",
]

_TARGET_KEYWORDS = {
    "marketing", "brand", "cmo", "communications", "comms",
    "ceo", "chief executive", "vp", "director",
}


async def find_decision_makers(
    company_name: str,
    domain: str,
    max_results: int = 6,
) -> list:
    """
    Return a list of decision-maker candidates.

    Each item:
        {
            "name":       str | None,
            "role":       str | None,
            "source":     str,          # "Hunter" | "Serper" | "Google"
            "source_url": str | None,
        }
    """
    results: list[dict] = []

    # ── 1. Hunter.io ─────────────────────────────────────────────────────────
    hunter_key: Optional[str] = os.getenv("HUNTER_API_KEY")
    if hunter_key and domain:
        results = await _hunter_search(domain, hunter_key, max_results)

    # ── 2. Serper LinkedIn (fills gaps) ──────────────────────────────────────
    if len(results) < max_results:
        serper_results = await _serper_linkedin_search(
            company_name, max_results - len(results)
        )
        results.extend(serper_results)

    # ── 3. googlesearch fallback ──────────────────────────────────────────────
    if len(results) < max_results:
        google_results = await _google_linkedin_search(
            company_name, max_results - len(results)
        )
        results.extend(google_results)

    logger.info(
        "[decision_makers] Found %d for '%s' (hunter=%d, serper=%d, google=%d)",
        len(results), company_name,
        sum(1 for r in results if r.get("source") == "Hunter"),
        sum(1 for r in results if r.get("source") == "Serper"),
        sum(1 for r in results if r.get("source") == "Google"),
    )
    return results[:max_results]


# ---------------------------------------------------------------------------
# Source 1 – Hunter.io
# ---------------------------------------------------------------------------

async def _hunter_search(domain: str, api_key: str, max_results: int) -> list:
    url = (
        f"https://api.hunter.io/v2/domain-search"
        f"?domain={domain}&api_key={api_key}&limit=20"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    logger.warning("[decision_makers] Hunter.io HTTP %s for %s", resp.status, domain)
                    return []
                data = await resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("[decision_makers] Hunter.io failed: %s", exc)
        return []

    emails = (data.get("data") or {}).get("emails", [])
    results = []
    for emp in emails:
        title: str = (emp.get("position") or emp.get("title") or "").lower()
        if not any(kw in title for kw in _TARGET_KEYWORDS):
            continue
        first = emp.get("first_name", "")
        last  = emp.get("last_name", "")
        full  = emp.get("full_name") or f"{first} {last}".strip()
        results.append({
            "name":       full or None,
            "role":       emp.get("position") or emp.get("title"),
            "source":     "Hunter",
            "source_url": None,
        })
        if len(results) >= max_results:
            break
    return results


# ---------------------------------------------------------------------------
# Source 2 – Serper LinkedIn search
# ---------------------------------------------------------------------------

async def _serper_linkedin_search(company_name: str, limit: int) -> list:
    """Use Serper to find LinkedIn profiles for target roles."""
    results = []
    seen_urls: set[str] = set()

    for role in _TARGET_ROLES:
        if len(results) >= limit:
            break
        query = f'site:linkedin.com/in "{company_name}" "{role}"'
        items = await serper_search(query, num_results=2)
        for item in items:
            url: str = item.get("link", "")
            if "linkedin.com/in/" not in url or url in seen_urls:
                continue
            seen_urls.add(url)
            slug = url.rstrip("/").split("/in/")[-1].split("?")[0]
            name_guess = slug.replace("-", " ").title() if slug else None
            results.append({
                "name":       name_guess,
                "role":       role,
                "source":     "Serper",
                "source_url": url,
            })
            break  # one per role

        await asyncio.sleep(0.2)  # stay within rate limits

    return results


# ---------------------------------------------------------------------------
# Source 3 – googlesearch fallback
# ---------------------------------------------------------------------------

async def _google_linkedin_search(company_name: str, limit: int) -> list:
    results = []
    seen_urls: set[str] = set()

    for role in _TARGET_ROLES:
        if len(results) >= limit:
            break
        query = f'site:linkedin.com/in "{company_name}" "{role}"'
        try:
            for url in search(query, num_results=2, sleep_interval=1):
                if "linkedin.com/in/" in url and url not in seen_urls:
                    seen_urls.add(url)
                    slug = url.rstrip("/").split("/in/")[-1].split("?")[0]
                    name_guess = slug.replace("-", " ").title() if slug else None
                    results.append({
                        "name":       name_guess,
                        "role":       role,
                        "source":     "Google",
                        "source_url": url,
                    })
                    break
        except Exception as exc:  # noqa: BLE001
            logger.warning("[decision_makers] googlesearch failed for role '%s': %s", role, exc)

        await asyncio.sleep(0.5)

    return results