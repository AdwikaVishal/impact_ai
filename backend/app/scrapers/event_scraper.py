"""
event_scraper.py – Find brand events, pop-ups, activations, and trade shows.

Because event data is unstructured, this scraper returns raw source URLs and
any text snippets it can extract. Person B's LLM layer will parse them into
structured records.

Main export:
  - find_events(company_name) -> list[dict]
"""

import asyncio
import logging
import re

from bs4 import BeautifulSoup
from googlesearch import search

from .base_scraper import clean_text, fetch_html

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

    try:
        for url in search(query, num_results=20, sleep_interval=1):
            if url in seen_urls:
                continue
            seen_urls.add(url)

            domain = _extract_domain(url)
            platform = domain if any(p in domain for p in _EVENT_PLATFORMS) else None

            candidates.append(
                {
                    "source_url": url,
                    "platform": platform,
                    "snippet": None,
                    "needs_parsing": True,
                }
            )

            if len(candidates) >= max_results:
                break
    except Exception as exc:  # noqa: BLE001
        logger.error("Google search failed for events of '%s': %s", company_name, exc)

    # Try to pull a short snippet from each URL (fire concurrently, best-effort)
    tasks = [_extract_snippet(c["source_url"]) for c in candidates]
    snippets = await asyncio.gather(*tasks, return_exceptions=True)

    for candidate, snippet in zip(candidates, snippets):
        if isinstance(snippet, str) and snippet:
            candidate["snippet"] = snippet

    logger.info("Found %d event candidates for '%s'", len(candidates), company_name)
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
