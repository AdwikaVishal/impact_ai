"""
competitor_analyzer.py – Generates Output #3 (Competitor Mapping with strengths & gaps)
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
    """Output #3: Competitor mapping with one strength and one gap per competitor."""
    if not competitors:
        return [{"name": "No competitors found", "strength": "Unknown", "gap": "Unknown"}]

    comp_text = ""
    for c in competitors[:5]:
        name = c.get("name", "Unknown")
        website = c.get("website", "")
        recent = c.get("recent_activity") or []
        recent_str = "; ".join(str(a) for a in recent[:2]) if recent else "No recent activity"
        comp_text += f"- {name} ({website}): {recent_str}\n"

    prompt = COMPETITOR_GAPS_PROMPT.format(
        company_name=company_name,
        category=category or "general",
        competitors_list=comp_text,
    )
    response = await get_llm().generate(prompt, max_tokens=600)
    logger.debug("[competitors] raw response: %s", response[:200])

    # Try to parse JSON array from response
    for pattern in [r"\[.*?\]", r"\[.*\]"]:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                if isinstance(parsed, list) and parsed:
                    return [
                        {
                            "name":     str(item.get("name", "Unknown")),
                            "strength": str(item.get("strength", "Not identified")),
                            "gap":      str(item.get("gap", "Not identified")),
                        }
                        for item in parsed
                        if isinstance(item, dict)
                    ][:5]
            except json.JSONDecodeError:
                continue

    # Fallback: return raw competitor names
    logger.warning("[competitors] could not parse JSON – using fallback")
    return [
        {
            "name":     c.get("name", "Unknown"),
            "strength": "Data available via API",
            "gap":      "Requires deeper analysis",
        }
        for c in competitors[:5]
    ]
