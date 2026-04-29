"""
decision_maker_scraper.py – Find marketing/brand decision-makers at a company.

Strategy:
  1. Hunter.io domain-search API (requires HUNTER_API_KEY in .env)
  2. Google search fallback (LinkedIn profile URLs)

Main export:
  - find_decision_makers(company_name, domain) -> list[dict]
"""

import asyncio
import logging
import os
from typing import Optional

import aiohttp
from googlesearch import search

logger = logging.getLogger(__name__)

# Roles we care about (marketing / brand / comms decision-makers)
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
    "marketing", "brand", "cmo", "communications", "comms", "ceo",
    "chief executive", "vp", "director",
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
            "source":     str,          # "Hunter" | "Google"
            "source_url": str | None,
        }
    """
    hunter_key: Optional[str] = os.getenv("HUNTER_API_KEY")

    results: list[dict] = []

    if hunter_key and domain:
        results = await _hunter_search(domain, hunter_key, max_results)

    # Always supplement with Google if Hunter returned fewer than max_results
    if len(results) < max_results:
        google_results = await _google_search(company_name, max_results - len(results))
        results.extend(google_results)

    logger.info(
        "Found %d decision-maker candidates for '%s'", len(results), company_name
    )
    return results[:max_results]


# ---------------------------------------------------------------------------
# Hunter.io
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
                    logger.warning("Hunter.io HTTP %s for domain %s", resp.status, domain)
                    return []
                data = await resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("Hunter.io request failed: %s", exc)
        return []

    emails = (data.get("data") or {}).get("emails", [])
    results = []
    for emp in emails:
        title: str = (emp.get("position") or emp.get("title") or "").lower()
        if not any(kw in title for kw in _TARGET_KEYWORDS):
            continue
        results.append(
            {
                "name": emp.get("full_name") or f"{emp.get('first_name','')} {emp.get('last_name','')}".strip(),
                "role": emp.get("position") or emp.get("title"),
                "source": "Hunter",
                "source_url": None,
            }
        )
        if len(results) >= max_results:
            break

    return results


# ---------------------------------------------------------------------------
# Google fallback
# ---------------------------------------------------------------------------

async def _google_search(company_name: str, max_results: int) -> list:
    """Search Google for LinkedIn profiles of target roles at the company."""
    results = []
    seen_urls: set[str] = set()

    for role in _TARGET_ROLES:
        if len(results) >= max_results:
            break
        query = f'site:linkedin.com/in "{company_name}" "{role}"'
        try:
            for url in search(query, num_results=2, sleep_interval=1):
                if "linkedin.com/in/" in url and url not in seen_urls:
                    seen_urls.add(url)
                    # Best-effort name extraction from URL slug
                    slug = url.rstrip("/").split("/in/")[-1].split("?")[0]
                    name_guess = slug.replace("-", " ").title() if slug else None
                    results.append(
                        {
                            "name": name_guess,
                            "role": role,
                            "source": "Google",
                            "source_url": url,
                        }
                    )
                    break  # one result per role is enough
        except Exception as exc:  # noqa: BLE001
            logger.warning("Google search failed for role '%s': %s", role, exc)

        await asyncio.sleep(0.5)  # be polite to Google

    return results
