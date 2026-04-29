"""
overview_generator.py – Generate company overview and market position text.

Exports:
  - generate_overview(about_text)                    -> str
  - generate_market_position(company_name, headlines) -> str
"""

import logging

from .llm_client import get_llm
from .prompts import COMPANY_OVERVIEW_PROMPT, MARKET_POSITION_PROMPT

logger = logging.getLogger(__name__)

_INSUFFICIENT = "Insufficient data to generate overview."
_NO_NEWS      = "No recent news available to assess market position."


async def generate_overview(about_text: str) -> str:
    """
    Summarise the company's business model, scale, and positioning.

    Returns a 2-3 sentence plain-text overview, or a 'no data' message.
    """
    if not about_text or len(about_text.strip()) < 50:
        logger.info("[overview] about_text too short – returning default")
        return _INSUFFICIENT

    prompt = COMPANY_OVERVIEW_PROMPT.format(about_text=about_text[:3000])
    result = await get_llm().generate(prompt, max_tokens=200)
    logger.info("[overview] generated (%d chars)", len(result))
    return result or _INSUFFICIENT


async def generate_market_position(company_name: str, news_headlines: list) -> str:
    """
    Describe current brand perception and recent strategic shifts based on news.

    Args:
        company_name:    Used in the prompt for context.
        news_headlines:  List of dicts with at least a 'title' and 'date' key.

    Returns:
        2-3 sentence plain-text analysis, or a 'no data' message.
    """
    if not news_headlines:
        logger.info("[market_position] no headlines for '%s'", company_name)
        return _NO_NEWS

    news_list = "\n".join(
        f"- {n.get('title', '')} ({n.get('date', 'n/d')})"
        for n in news_headlines[:10]
        if n.get("title")
    )
    if not news_list.strip():
        return _NO_NEWS

    prompt = MARKET_POSITION_PROMPT.format(
        company_name=company_name,
        news_list=news_list,
    )
    result = await get_llm().generate(prompt, max_tokens=250)
    logger.info("[market_position] generated for '%s' (%d chars)", company_name, len(result))
    return result or _NO_NEWS
