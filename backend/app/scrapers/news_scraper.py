"""
news_scraper.py – Fetch recent news headlines for a company.

Primary source:  NewsAPI (free tier – set NEWS_API_KEY in .env)
Fallback source: Google News RSS feed (no key required)

Main export:
  - get_news_headlines(company_name, days_back) -> list[dict]
"""

import asyncio
import logging
import os
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

from .base_scraper import clean_text, fetch_html

logger = logging.getLogger(__name__)

_NEWSAPI_BASE = "https://newsapi.org/v2/everything"
_GNEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


async def get_news_headlines(
    company_name: str,
    days_back: int = 365,
    max_articles: int = 20,
) -> list:
    """
    Return a list of recent news articles about *company_name*.

    Each item:
        {
            "title":   str,
            "date":    str  (YYYY-MM-DD),
            "source":  str,
            "url":     str,
            "summary": str | None,
        }

    Tries NewsAPI first; falls back to Google News RSS.
    """
    api_key: Optional[str] = os.getenv("NEWS_API_KEY")

    if api_key:
        articles = await _fetch_newsapi(company_name, api_key, days_back, max_articles)
        if articles:
            return articles
        logger.warning("NewsAPI returned no results – falling back to Google News RSS")

    return await _fetch_google_news_rss(company_name, max_articles)


# ---------------------------------------------------------------------------
# NewsAPI implementation
# ---------------------------------------------------------------------------

async def _fetch_newsapi(
    company_name: str,
    api_key: str,
    days_back: int,
    max_articles: int,
) -> list:
    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    params = {
        "q": company_name,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": max_articles,
        "apiKey": api_key,
    }
    url = f"{_NEWSAPI_BASE}?{urllib.parse.urlencode(params)}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    logger.warning("NewsAPI HTTP %s", resp.status)
                    return []
                data = await resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("NewsAPI request failed: %s", exc)
        return []

    articles = data.get("articles", [])
    return [
        {
            "title": art.get("title", ""),
            "date": (art.get("publishedAt") or "")[:10],
            "source": (art.get("source") or {}).get("name", ""),
            "url": art.get("url", ""),
            "summary": art.get("description"),
        }
        for art in articles
        if art.get("title")
    ]


# ---------------------------------------------------------------------------
# Google News RSS fallback
# ---------------------------------------------------------------------------

async def _fetch_google_news_rss(company_name: str, max_articles: int) -> list:
    """Parse Google News RSS – no API key required."""
    query = urllib.parse.quote_plus(company_name)
    url = _GNEWS_RSS.format(query=query)

    html = await fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml-xml")  # lxml XML parser for RSS
    items = soup.find_all("item")[:max_articles]

    results = []
    for item in items:
        title_tag = item.find("title")
        link_tag = item.find("link")
        pub_date_tag = item.find("pubDate")
        source_tag = item.find("source")

        title = clean_text(title_tag.get_text()) if title_tag else ""
        link = link_tag.get_text(strip=True) if link_tag else ""
        pub_date = _parse_rss_date(pub_date_tag.get_text(strip=True) if pub_date_tag else "")
        source = source_tag.get_text(strip=True) if source_tag else "Google News"

        if title:
            results.append(
                {
                    "title": title,
                    "date": pub_date,
                    "source": source,
                    "url": link,
                    "summary": None,
                }
            )

    logger.info("Google News RSS returned %d articles for '%s'", len(results), company_name)
    return results


def _parse_rss_date(raw: str) -> str:
    """Convert RSS date string to YYYY-MM-DD; return raw string on failure."""
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw[:10] if len(raw) >= 10 else raw
