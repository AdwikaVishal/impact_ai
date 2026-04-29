"""
competitor_analyzer.py – Analyse competitor strengths and gaps using LLM.

Export:
  - analyze_competitors(company_name, category, competitors) -> list[dict]

Each returned dict:
    {
        "name":     str,
        "strength": str,
        "gap":      str,
    }
"""

import json
import logging
import re

from .llm_client import get_llm
from .prompts import COMPETITOR_GAPS_PROMPT

logger = logging.getLogger(__name__)


async def analyze_competitors(
    company_name: str,
    category: str,
    competitors: list,
) -> list:
    """
    Use the LLM to identify one strength and one gap for each competitor.

    Falls back gracefully if the LLM returns malformed JSON.
    """
    if not competitors:
        logger.info("[competitors] no competitors to analyse for '%s'", company_name)
        return []

    # Build a compact text representation of each competitor
    comp_lines = []
    for c in competitors:
        activity = c.get("recent_activity") or []
        activity_str = "; ".join(str(a) for a in activity[:2]) if activity else "no recent activity found"
        comp_lines.append(f"- {c.get('name', 'Unknown')}: {activity_str}")
    competitors_list = "\n".join(comp_lines)

    prompt = COMPETITOR_GAPS_PROMPT.format(
        company_name=company_name,
        category=category or "general",
        competitors_list=competitors_list,
    )

    response = await get_llm().generate(prompt, max_tokens=700)
    logger.debug("[competitors] raw LLM response: %s", response[:200])

    return _parse_competitor_json(response, competitors)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _parse_competitor_json(response: str, raw_competitors: list) -> list:
    """
    Try to extract a JSON array from the LLM response.
    Falls back to a structured placeholder if parsing fails.
    """
    # 1. Try direct parse
    try:
        data = json.loads(response.strip())
        if isinstance(data, list):
            return _validate_items(data)
    except json.JSONDecodeError:
        pass

    # 2. Try to find a JSON array anywhere in the response
    match = re.search(r"\[.*?\]", response, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, list):
                return _validate_items(data)
        except json.JSONDecodeError:
            pass

    # 3. Fallback: return raw competitor names with the LLM text as strength
    logger.warning("[competitors] could not parse JSON from LLM – using fallback")
    return [
        {
            "name":     c.get("name", "Unknown"),
            "strength": "See raw LLM output",
            "gap":      response[:120] if len(response) < 120 else response[:120] + "…",
        }
        for c in raw_competitors[:5]
    ]


def _validate_items(items: list) -> list:
    """Ensure each item has the required keys; fill missing ones with 'N/A'."""
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        result.append({
            "name":     str(item.get("name", "Unknown")),
            "strength": str(item.get("strength", "Not identified")),
            "gap":      str(item.get("gap", "Not identified")),
        })
    return result
