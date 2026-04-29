"""
event_scraper.py – Find brand events, pop-ups, activations, and trade shows.

Because event data is unstructured, this scraper returns raw source URLs and
any text snippets it can extract. Person B's LLM layer will parse them into
structured records.

Source priority:
  1. Serper  – cleaner results, snippet included (set SERPER_KEY in .env)
  2. googlesearch-python fallback

Main export:
  - find_events(company_name) -> list[dict]
"""

import asyncio
import logging
import re

from bs4 import BeautifulSoup
from googlesearch import search

from .base import clean_text, fetch_html
from .serper_helper import serper_search

logger = logging.getLogger(__name__)

# Event-platform domains we prioritise
_EVENT_PLATFORMS = {"eventbrite.com", "lu.ma", "luma.events", "meetup.com", "hopin.com"}

# Keywords that suggest an event-related page
_EVENT_KEYWORDS = re.compile(
    r"\b(event|pop.?up|activation|trade.?show|conference|summit|expo|launch|festival|workshop)\b",
    re.I,
)


async def find_events(
    company_name: str,
    max_results: int = 8,
) -> list:
    """
    Return a list of event candidates for *company_name*.

    Each item:
        {
            "source_url":    str,
            "platform":      str | None,   # e.g. "eventbrite.com"
            "snippet":       str | None,   # any text extracted from the page
            "needs_parsing": bool,         # True → Person B should parse with LLM
        }
    """
    query = f"{company_name} event pop-up activation trade show 2024 2025"
    candidates: list[dict] = []
    seen_urls: set[str] = set()

    # ── 1. Serper (includes snippets for free) ───────────────────────────────
    serper_items = await serper_search(query, num_results=max_results + 5)
    for item in serper_items:
        url: str = item.get("link", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        domain = _extract_domain(url)
        platform = domain if any(p in domain for p in _EVENT_PLATFORMS) else None
        candidates.append({
            "source_url":    url,
            "platform":      platform,
            "snippet":       item.get("snippet") or None,
            "needs_parsing": True,
        })
        if len(candidates) >= max_results:
            break

    # ── 2. googlesearch fallback ─────────────────────────────────────────────
    if len(candidates) < max_results:
        try:
            for url in search(query, num_results=20, sleep_interval=1):
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                domain = _extract_domain(url)
                platform = domain if any(p in domain for p in _EVENT_PLATFORMS) else None
                candidates.append({
                    "source_url":    url,
                    "platform":      platform,
                    "snippet":       None,
                    "needs_parsing": True,
                })
                if len(candidates) >= max_results:
                    break
        except Exception as exc:  # noqa: BLE001
            logger.error("[events] googlesearch failed for '%s': %s", company_name, exc)

    # ── Enrich missing snippets by fetching the page ─────────────────────────
    async def _maybe_fetch(c: dict) -> str:
        if c["snippet"]:
            return c["snippet"]
        return await _extract_snippet(c["source_url"])

    snippets = await asyncio.gather(*[_maybe_fetch(c) for c in candidates], return_exceptions=True)
    for candidate, snippet in zip(candidates, snippets):
        if isinstance(snippet, str) and snippet and not candidate["snippet"]:
            candidate["snippet"] = snippet

    logger.info("[events] Found %d candidates for '%s'", len(candidates), company_name)
    return candidates


async def _extract_snippet(url: str) -> str:
    """Fetch a page and return the first event-related sentence (≤ 300 chars)."""
    html = await fetch_html(url, timeout=8)
    if not html:
        return ""

    soup = BeautifulSoup(html, "lxml")
    # Remove nav/footer noise
    for tag in soup.select("nav, footer, header, script, style"):
        tag.decompose()

    text = clean_text(soup.get_text(separator=" "))

    # Find the first sentence that contains an event keyword
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if _EVENT_KEYWORDS.search(sentence):
            return sentence[:300]

    return text[:300]


def _extract_domain(url: str) -> str:
    try:
        domain = url.split("//")[-1].split("/")[0].lower()
        return domain.removeprefix("www.")
    except Exception:
        return url
