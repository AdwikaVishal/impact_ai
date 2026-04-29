"""
watchout_generator.py – Generates Output #6 (Strategic Watchouts)
"""

import json
import logging
import re

from .llm_client import get_llm
from .prompts import WATCHOUTS_PROMPT

logger = logging.getLogger(__name__)


async def generate_watchouts(
    company_name: str,
    news: list,
    competitors: list,
    events: list,
) -> list:
    """Output #6: 3 strategic watchouts grounded in scraped data."""
    news_summary = "\n".join(
        f"- {n.get('title', '')}" for n in news[:5] if n.get("title")
    ) or "No recent news available"

    competitor_names = [c.get("name", "") for c in competitors[:3] if c.get("name")]
    competitor_summary = ", ".join(competitor_names) if competitor_names else "No competitor data"

    event_summary = "\n".join(
        f"- {e.get('source_url', '')[:60]}" for e in events[:3] if e.get("source_url")
    ) or "No event data available"

    prompt = WATCHOUTS_PROMPT.format(
        company_name=company_name,
        news_summary=news_summary,
        competitor_summary=competitor_summary,
        events_summary=event_summary,
    )
    response = await get_llm().generate(prompt, max_tokens=300)
    logger.debug("[watchouts] raw response for '%s': %s", company_name, response[:200])

    # Try to parse JSON array
    match = re.search(r"\[.*\]", response, re.DOTALL)
    if match:
        try:
            watchouts = json.loads(match.group())
            if isinstance(watchouts, list) and watchouts:
                return [str(w) for w in watchouts[:3]]
        except json.JSONDecodeError:
            pass

    # Fallback: build from available data
    logger.warning("[watchouts] could not parse JSON for '%s' – using fallback", company_name)
    fallback = []
    if len(competitors) >= 2:
        names = ", ".join(c.get("name", "") for c in competitors[:2])
        fallback.append(f"Increasing competitive pressure from {names}")
    if news:
        fallback.append("Recent news signals potential market shifts requiring close monitoring")
    fallback.append("Brand perception and share-of-voice should be tracked continuously")
    return fallback[:3]
