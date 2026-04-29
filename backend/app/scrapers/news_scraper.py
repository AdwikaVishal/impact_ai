"""
news_scraper.py – Fetch recent news headlines for a company.

Source priority (highest → lowest):
  1. gnews package          – free, no key, reliable Google News wrapper
  2. NewsAPI                – set NEWS_API_KEY in .env for richer metadata
  3. Newsdata.io            – set NEWSDATA_API_KEY in .env as extra fallback
  4. Google News RSS        – raw RSS parse, always available, no key needed

Main export:
  - get_news_headlines(company_name, days_back, max_articles) -> list[dict]
"""

import asyncio
import logging
import os
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup
from gnews import GNews

from .base_scraper import clean_text, fetch_html

logger = logging.getLogger(__name__)

_NEWSAPI_BASE   = "https://newsapi.org/v2/everything"
_NEWSDATA_BASE  = "https://newsdata.io/api/1/news"
_GNEWS_RSS_URL  = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


async def get_news_headlines(
    company_name: str,
    days_back: int = 365,
    max_articles: int = 20,
) -> list:
    """
    Return up to *max_articles* recent news items about *company_name*.

    Each item:
        {
            "title":   str,
            "date":    str  (YYYY-MM-DD),
            "source":  str,
            "url":     str,
            "summary": str | None,
        }
    """
    # ── 1. gnews (primary – free, no key) ───────────────────────────────────
    articles = await _fetch_gnews(company_name, days_back, max_articles)
    if articles:
        logger.info("[news] gnews returned %d articles for '%s'", len(articles), company_name)
        return articles

    # ── 2. NewsAPI (if key present) ──────────────────────────────────────────
    newsapi_key: Optional[str] = os.getenv("NEWS_API_KEY")
    if newsapi_key:
        articles = await _fetch_newsapi(company_name, newsapi_key, days_back, max_articles)
        if articles:
            logger.info("[news] NewsAPI returned %d articles for '%s'", len(articles), company_name)
            return articles
        logger.warning("[news] NewsAPI returned nothing – trying next source")

    # ── 3. Newsdata.io (if key present) ─────────────────────────────────────
    newsdata_key: Optional[str] = os.getenv("NEWSDATA_API_KEY")
    if newsdata_key:
        articles = await _fetch_newsdata(company_name, newsdata_key, max_articles)
        if articles:
            logger.info("[news] Newsdata.io returned %d articles for '%s'", len(articles), company_name)
            return articles
        logger.warning("[news] Newsdata.io returned nothing – falling back to RSS")

    # ── 4. Google News RSS (always-available last resort) ────────────────────
    articles = await _fetch_google_news_rss(company_name, max_articles)
    logger.info("[news] Google News RSS returned %d articles for '%s'", len(articles), company_name)
    return articles


# ---------------------------------------------------------------------------
# 1. gnews
# ---------------------------------------------------------------------------

async def _fetch_gnews(company_name: str, days_back: int, max_articles: int) -> list:
    """
    Use the gnews package to query Google News.
    gnews is synchronous, so we run it in a thread pool to avoid blocking.
    """
    def _sync_fetch() -> list:
        try:
            period = _days_to_gnews_period(days_back)
            gn = GNews(language="en", period=period, max_results=max_articles)
            raw = gn.get_news(company_name)
            results = []
            for art in raw:
                results.append({
                    "title":   art.get("title", ""),
                    "date":    _normalise_date(art.get("published date", "")),
                    "source":  (art.get("publisher") or {}).get("title", "Google News"),
                    "url":     art.get("url", ""),
                    "summary": art.get("description"),
                })
            return results
        except Exception as exc:  # noqa: BLE001
            logger.warning("[news] gnews failed: %s", exc)
            return []

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_fetch)


def _days_to_gnews_period(days: int) -> str:
    """Convert a day count to a gnews period string like '7d', '1m', '1y'."""
    if days <= 7:
        return f"{days}d"
    if days <= 30:
        return f"{days // 7}w"
    if days <= 365:
        return f"{days // 30}m"
    return "1y"


# ---------------------------------------------------------------------------
# 2. NewsAPI
# ---------------------------------------------------------------------------

async def _fetch_newsapi(
    company_name: str,
    api_key: str,
    days_back: int,
    max_articles: int,
) -> list:
    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    params = {
        "q":        company_name,
        "from":     from_date,
        "sortBy":   "publishedAt",
        "language": "en",
        "pageSize": max_articles,
        "apiKey":   api_key,
    }
    url = f"{_NEWSAPI_BASE}?{urllib.parse.urlencode(params)}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    logger.warning("[news] NewsAPI HTTP %s", resp.status)
                    return []
                data = await resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("[news] NewsAPI request failed: %s", exc)
        return []

    return [
        {
            "title":   art.get("title", ""),
            "date":    (art.get("publishedAt") or "")[:10],
            "source":  (art.get("source") or {}).get("name", ""),
            "url":     art.get("url", ""),
            "summary": art.get("description"),
        }
        for art in data.get("articles", [])
        if art.get("title")
    ]


# ---------------------------------------------------------------------------
# 3. Newsdata.io
# ---------------------------------------------------------------------------

async def _fetch_newsdata(company_name: str, api_key: str, max_articles: int) -> list:
    params = {
        "q":        company_name,
        "language": "en",
        "apikey":   api_key,
    }
    url = f"{_NEWSDATA_BASE}?{urllib.parse.urlencode(params)}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    logger.warning("[news] Newsdata.io HTTP %s", resp.status)
                    return []
                data = await resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("[news] Newsdata.io request failed: %s", exc)
        return []

    return [
        {
            "title":   art.get("title", ""),
            "date":    (art.get("pubDate") or "")[:10],
            "source":  art.get("source_id", ""),
            "url":     art.get("link", ""),
            "summary": art.get("description"),
        }
        for art in data.get("results", [])[:max_articles]
        if art.get("title")
    ]


# ---------------------------------------------------------------------------
# 4. Google News RSS (last resort)
# ---------------------------------------------------------------------------

async def _fetch_google_news_rss(company_name: str, max_articles: int) -> list:
    query = urllib.parse.quote_plus(company_name)
    url = _GNEWS_RSS_URL.format(query=query)

    html = await fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml-xml")
    items = soup.find_all("item")[:max_articles]
    results = []
    for item in items:
        title_tag    = item.find("title")
        link_tag     = item.find("link")
        pub_date_tag = item.find("pubDate")
        source_tag   = item.find("source")

        title = clean_text(title_tag.get_text()) if title_tag else ""
        if not title:
            continue
        results.append({
            "title":   title,
            "date":    _parse_rss_date(pub_date_tag.get_text(strip=True) if pub_date_tag else ""),
            "source":  source_tag.get_text(strip=True) if source_tag else "Google News",
            "url":     link_tag.get_text(strip=True) if link_tag else "",
            "summary": None,
        })
    return results


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _normalise_date(raw: str) -> str:
    """Try several common date formats and return YYYY-MM-DD."""
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw[:10] if len(raw) >= 10 else raw


def _parse_rss_date(raw: str) -> str:
    return _normalise_date(raw)
