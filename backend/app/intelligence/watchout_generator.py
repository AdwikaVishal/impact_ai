"""
watchout_generator.py – Generate strategic watchouts for a brand.

Export:
  - generate_watchouts(company_name, news, competitors, events) -> list[str]

Returns a list of 3 plain-text bullet strings (without the leading dash).
"""

import logging
import re

from .llm_client import get_llm
from .prompts import STRATEGIC_WATCHOUTS_PROMPT

logger = logging.getLogger(__name__)

_DEFAULT_WATCHOUT = "Insufficient data to generate strategic watchouts."


async def generate_watchouts(
    company_name: str,
    news: list,
    competitors: list,
    events: list,
) -> list:
    """
    Identify 3 strategic risks or blind spots based on scraped data.

    Returns a list of strings (one per watchout).
    """
    news_summary = (
        "\n".join(f"- {n.get('title', '')}" for n in news[:6] if n.get("title"))
        or "No recent news available"
    )
    competitor_summary = (
        ", ".join(c.get("name", "") for c in competitors[:4] if c.get("name"))
        or "No competitor data available"
    )
    events_summary = (
        "; ".join(
            e.get("snippet") or e.get("source_url", "")
            for e in events[:3]
            if e.get("snippet") or e.get("source_url")
        )
        or "No event data available"
    )

    prompt = STRATEGIC_WATCHOUTS_PROMPT.format(
        company_name=company_name,
        news_summary=news_summary,
        competitor_summary=competitor_summary,
        events_summary=events_summary,
    )

    response = await get_llm().generate(prompt, max_tokens=350)
    logger.debug("[watchouts] raw response for '%s': %s", company_name, response[:200])

    watchouts = _parse_bullets(response)
    if not watchouts:
        logger.warning("[watchouts] no bullets parsed for '%s'", company_name)
        return [_DEFAULT_WATCHOUT]

    logger.info("[watchouts] generated %d watchouts for '%s'", len(watchouts), company_name)
    return watchouts


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _parse_bullets(text: str) -> list:
    """
    Extract bullet-point lines from LLM output.
    Handles '- ', '• ', '* ', and numbered lists like '1. '.
    """
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        # Match common bullet formats
        cleaned = re.sub(r"^[-•*]\s+|^\d+\.\s+", "", stripped).strip()
        if cleaned and len(cleaned) > 10:
            lines.append(cleaned)
    return lines[:3]  # cap at 3 as specified in the prompt
