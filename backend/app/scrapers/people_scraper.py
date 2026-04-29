"""
people_scraper.py – Compatibility alias for decision_maker_scraper.

The canonical implementation lives in decision_maker_scraper.py.
This module re-exports everything so code that imports from people_scraper
continues to work.
"""

from .decision_maker_scraper import (  # noqa: F401
    find_decision_makers,
    find_decision_makers as find_people,  # legacy alias
    _TARGET_ROLES,
)

__all__ = ["find_decision_makers", "find_people", "_TARGET_ROLES"]
