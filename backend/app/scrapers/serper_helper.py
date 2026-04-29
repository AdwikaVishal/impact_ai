"""
serper_helper.py – Shared Serper API utilities.

Serper is a Google Search API with a free tier (2 500 requests/month).
Set SERPER_KEY in .env to enable.

Main export:
  - serper_search(query, num_results) -> list[dict]
"""

import logging
import os
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

_SERPER_URL = "https://google.serper.dev/search"


async def serper_search(query: str, num_results: int = 10) -> list:
    """
    Query Serper and return organic search results.

    Returns:
        [
            {
                "title":    str,
                "link":     str,
                "snippet":  str,
                "position": int,
            },
            ...
        ]
    """
    api_key: Optional[str] = os.getenv("SERPER_KEY")
    if not api_key:
        logger.debug("[serper] SERPER_KEY not set – skipping")
        return []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                _SERPER_URL,
                json={"q": query, "num": num_results},
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    logger.warning("[serper] HTTP %s for query '%s'", resp.status, query)
                    return []
                data = await resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("[serper] request failed: %s", exc)
        return []

    return [
        {
            "title":    item.get("title", ""),
            "link":     item.get("link", ""),
            "snippet":  item.get("snippet", ""),
            "position": item.get("position", 0),
        }
        for item in data.get("organic", [])
    ]