"""
Scrapers package – data collection modules for Impact AI.

Exports the main async functions used by the research orchestrator.
"""

from .company_scraper import get_company_website, scrape_about_page
from .news_scraper import get_news_headlines
from .competitor_scraper import find_competitors
from .event_scraper import find_events
from .decision_maker_scraper import find_decision_makers
from .contact_scraper import enrich_contacts

__all__ = [
    "get_company_website",
    "scrape_about_page",
    "get_news_headlines",
    "find_competitors",
    "find_events",
    "find_decision_makers",
    "enrich_contacts",
]
