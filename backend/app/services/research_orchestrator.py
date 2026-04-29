"""
research_orchestrator.py – Coordinate all scrapers and return a unified raw-data dict.

This is the single entry point that Person B and Person C consume.
Call collect_raw_data() to get everything in one shot.
"""

import asyncio
import logging
from typing import Any

from ..scrapers import (
    enrich_contacts,
    find_competitors,
    find_decision_makers,
    find_events,
    get_company_website,
    get_news_headlines,
    scrape_about_page,
)

logger = logging.getLogger(__name__)


async def collect_raw_data(company_name: str, category: str) -> dict[str, Any]:
    """
    Run all scrapers concurrently (where possible) and return the raw data schema.

    Schema:
    {
        "company_name":   str,
        "category":       str,
        "website":        str,
        "overview": {
            "about_text":       str,
            "scale_indicators": list[str],
            "founded":          str | None,
        },
        "market_perception": {
            "recent_news_headlines": list[{title, date, source, url}],
            "reviews":               list,   # placeholder – extend as needed
        },
        "competitors":        list[{name, website, recent_activity}],
        "brand_activity":     list[{title, date, source, url}],
        "events":             list[{source_url, platform, snippet, needs_parsing}],
        "decision_makers_raw": list[{name, role, source, source_url}],
        "contacts_raw":        list[{name, role, email_guesses, linkedin_url}],
        "_errors":             dict,   # keys = scraper name, values = error messages
    }
    """
    errors: dict[str, str] = {}

    # ── Step 1: website (needed by later scrapers) ──────────────────────────
    website = ""
    try:
        website = await get_company_website(company_name, category)
        logger.info("[%s] website: %s", company_name, website or "(not found)")
    except Exception as exc:  # noqa: BLE001
        errors["company_website"] = str(exc)
        logger.error("[%s] company_website failed: %s", company_name, exc)

    # ── Step 2: run independent scrapers concurrently ───────────────────────
    about_task = _safe(scrape_about_page(website) if website else _empty_about(), "about_page", errors)
    news_task = _safe(get_news_headlines(company_name), "news", errors)
    competitors_task = _safe(find_competitors(company_name, category), "competitors", errors)
    events_task = _safe(find_events(company_name), "events", errors)

    about_data, news, competitors, events = await asyncio.gather(
        about_task, news_task, competitors_task, events_task
    )

    # ── Step 3: decision-makers (needs domain from website) ─────────────────
    domain = _extract_domain(website)
    decision_makers = await _safe(
        find_decision_makers(company_name, domain), "decision_makers", errors
    )

    # ── Step 4: contact enrichment (needs decision-makers + domain) ─────────
    contacts = await _safe(
        enrich_contacts(decision_makers or [], domain), "contacts", errors
    )

    # ── Assemble output ──────────────────────────────────────────────────────
    scale_indicators = []
    if about_data:
        if about_data.get("revenue"):
            scale_indicators.append(f"Revenue: {about_data['revenue']}")
        if about_data.get("employees"):
            scale_indicators.append(f"Employees: {about_data['employees']}")

    result = {
        "company_name": company_name,
        "category": category,
        "website": website,
        "overview": {
            "about_text": (about_data or {}).get("about_text", ""),
            "scale_indicators": scale_indicators,
            "founded": (about_data or {}).get("founded"),
        },
        "market_perception": {
            "recent_news_headlines": [
                {"title": n["title"], "date": n["date"], "source": n.get("source", ""), "url": n.get("url", "")}
                for n in (news or [])
            ],
            "reviews": [],  # extend with Trustpilot / G2 scraper if needed
        },
        "competitors": competitors or [],
        "brand_activity": news or [],   # full news objects reused as brand activity
        "events": events or [],
        "decision_makers_raw": decision_makers or [],
        "contacts_raw": contacts or [],
        "_errors": errors,
    }

    logger.info(
        "[%s] collection complete – %d news, %d competitors, %d events, %d contacts",
        company_name,
        len(result["market_perception"]["recent_news_headlines"]),
        len(result["competitors"]),
        len(result["events"]),
        len(result["contacts_raw"]),
    )
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _safe(coro, name: str, errors: dict):
    """Await *coro* and catch exceptions, logging them into *errors*."""
    try:
        return await coro
    except Exception as exc:  # noqa: BLE001
        errors[name] = str(exc)
        logger.error("Scraper '%s' failed: %s", name, exc)
        return None


async def _empty_about() -> dict:
    return {"about_text": "", "revenue": None, "employees": None, "founded": None}


def _extract_domain(url: str) -> str:
    """Return bare domain (no scheme, no www., no path)."""
    try:
        domain = url.split("//")[-1].split("/")[0].lower()
        return domain.removeprefix("www.")
    except Exception:
        return ""
