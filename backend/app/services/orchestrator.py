"""
orchestrator.py – Unified data collection pipeline.

Calls all scrapers concurrently and returns the canonical raw-data schema.
Results are cached for CACHE_TTL seconds (default 1 hour) to avoid
re-scraping the same company within a session.

This is the single entry point for Person 2 (ML) and Person 3 (Frontend).
"""

import asyncio
import logging
from typing import Any

from aiocache import cached
from aiocache.serializers import JsonSerializer

from ..core.config import settings
from ..scrapers.base import extract_domain, find_website
from ..scrapers.company_scraper import scrape_about_page
from ..scrapers.competitor_scraper import find_competitors
from ..scrapers.contact_scraper import enrich_contacts
from ..scrapers.decision_maker_scraper import find_decision_makers
from ..scrapers.event_scraper import find_events
from ..scrapers.news_scraper import get_news_headlines

logger = logging.getLogger(__name__)


@cached(ttl=settings.CACHE_TTL, serializer=JsonSerializer())
async def collect_raw_data(company_name: str, category: str) -> dict[str, Any]:
    """
    Run the full scraping pipeline and return the unified raw-data schema.

    Cached for CACHE_TTL seconds so repeated calls within a session are instant.

    Schema
    ------
    {
        "company_name":  str,
        "category":      str,
        "website":       str,
        "domain":        str | None,
        "overview": {
            "about_text":       str,
            "scale_indicators": {
                "revenue":   str | None,
                "employees": str | None,
                "founded":   str | None,
            },
        },
        "market_perception": {
            "recent_news_headlines": list[{title, date, source, url}],
            "reviews":               list,
        },
        "competitors":         list[{name, website, source, recent_activity}],
        "brand_activity":      list[{title, date, source, url, summary}],
        "events":              list[{source_url, platform, snippet, needs_parsing}],
        "decision_makers_raw": list[{name, role, source, source_url}],
        "contacts_raw":        list[{name, role, email_guesses, linkedin_url}],
        "_errors":             dict,
    }
    """
    errors: dict[str, str] = {}

    # ── Step 1: website + domain ─────────────────────────────────────────────
    website = ""
    domain = None
    try:
        website = await find_website(company_name, category)
        domain = extract_domain(website) if website else None
        logger.info("[%s] website=%s domain=%s", company_name, website or "(none)", domain)
    except Exception as exc:  # noqa: BLE001
        errors["website"] = str(exc)
        logger.error("[%s] website lookup failed: %s", company_name, exc)

    # ── Step 2: independent scrapers in parallel ─────────────────────────────
    about_coro = scrape_about_page(website) if website else _empty_about()
    about_data, news, competitors, events = await asyncio.gather(
        _safe(about_coro,                              "about_page",   errors),
        _safe(get_news_headlines(company_name),        "news",         errors),
        _safe(find_competitors(company_name, category),"competitors",  errors),
        _safe(find_events(company_name),               "events",       errors),
    )

    # ── Step 3: decision-makers (needs domain) ───────────────────────────────
    decision_makers = await _safe(
        find_decision_makers(company_name, domain or ""),
        "decision_makers",
        errors,
    )

    # ── Step 4: contact enrichment (needs decision-makers + domain) ──────────
    contacts = await _safe(
        enrich_contacts(decision_makers or [], domain or ""),
        "contacts",
        errors,
    )

    # ── Assemble ─────────────────────────────────────────────────────────────
    about = about_data or {}
    news_list = news or []

    return {
        "company_name": company_name,
        "category": category,
        "website": website,
        "domain": domain,
        "overview": {
            "about_text": about.get("about_text", ""),
            "scale_indicators": {
                "revenue":   about.get("revenue"),
                "employees": about.get("employees"),
                "founded":   about.get("founded"),
            },
        },
        "market_perception": {
            "recent_news_headlines": [
                {
                    "title":  n.get("title", ""),
                    "date":   n.get("date", ""),
                    "source": n.get("source", ""),
                    "url":    n.get("url", ""),
                }
                for n in news_list
            ],
            "reviews": [],
        },
        "competitors":         competitors or [],
        "brand_activity":      news_list,
        "events":              events or [],
        "decision_makers_raw": decision_makers or [],
        "contacts_raw":        contacts or [],
        "_errors":             errors,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _safe(coro, name: str, errors: dict):
    try:
        return await coro
    except Exception as exc:  # noqa: BLE001
        errors[name] = str(exc)
        logger.error("Scraper '%s' failed: %s", name, exc)
        return None


async def _empty_about() -> dict:
    return {"about_text": "", "revenue": None, "employees": None, "founded": None}
