"""
overview_generator.py – Generates Output #1 (Company Overview) and Output #2 (Market Position)
"""

import logging

from .llm_client import get_llm
from .prompts import MARKET_POSITION_PROMPT, OVERVIEW_PROMPT

logger = logging.getLogger(__name__)


async def generate_company_overview(about_text: str) -> str:
    """Output #1: 3-4 sentence company overview from about-page text."""
    if not about_text or len(about_text.strip()) < 100:
        return "Insufficient company data available. Please check the company website."

    prompt = OVERVIEW_PROMPT.format(about_text=about_text[:3000])
    result = await get_llm().generate(prompt, max_tokens=250)
    result = result.replace("```", "").strip()
    logger.info("[overview] generated (%d chars)", len(result))
    return result or "Company overview could not be generated."


async def generate_market_position(company_name: str, news_headlines: list) -> str:
    """Output #2: 2-3 sentence market position analysis from recent news."""
    if not news_headlines:
        return f"No recent news available for {company_name} to assess market position."

    news_text = "\n".join(
        f"- {n.get('title', '')} ({n.get('date', 'unknown date')})"
        for n in news_headlines[:10]
        if n.get("title")
    )
    if not news_text.strip():
        return f"No recent news available for {company_name} to assess market position."

    prompt = MARKET_POSITION_PROMPT.format(
        company_name=company_name,
        news_list=news_text,
    )
    result = await get_llm().generate(prompt, max_tokens=200)
    logger.info("[market_position] generated for '%s' (%d chars)", company_name, len(result))
    return result or f"Market position for {company_name} could not be analyzed."
