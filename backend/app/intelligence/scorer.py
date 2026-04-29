"""
scorer.py – Rule-based opportunity scoring (no LLM required).

Scores a company 0-100 based on signals that indicate outreach potential:
  - Recent campaign / launch activity in news
  - Number of known events / activations
  - Competitor pressure (more active competitors = more urgency)
  - Decision-maker data quality (named contacts = easier outreach)

Export:
  - compute_opportunity_score(news, events, competitors, contacts) -> int
  - score_breakdown(news, events, competitors, contacts)           -> dict
"""

import logging
import re

logger = logging.getLogger(__name__)

# Keywords that suggest active marketing / campaign spend
_CAMPAIGN_KEYWORDS = re.compile(
    r"\b(launch|campaign|rebrand|partnership|collab|activation|pop.?up|"
    r"new product|new collection|sponsorship|ambassador|event|festival)\b",
    re.I,
)

# Keywords that suggest negative sentiment / risk (reduce score slightly)
_RISK_KEYWORDS = re.compile(
    r"\b(lawsuit|recall|scandal|controversy|decline|layoff|bankruptcy|"
    r"investigation|fine|penalty)\b",
    re.I,
)


def compute_opportunity_score(
    news: list,
    events: list,
    competitors: list,
    contacts: list | None = None,
) -> int:
    """
    Return an integer 0-100 representing outreach opportunity strength.

    Higher = more signals that the brand is actively spending on marketing
    and that an agency approach is timely.
    """
    breakdown = score_breakdown(news, events, competitors, contacts or [])
    total = sum(breakdown.values())
    score = min(max(total, 0), 100)
    logger.info("[scorer] opportunity score=%d breakdown=%s", score, breakdown)
    return score


def score_breakdown(
    news: list,
    events: list,
    competitors: list,
    contacts: list,
) -> dict:
    """
    Return the individual score components (useful for debugging / UI display).

    Components (max points):
      campaign_activity  30  – news titles containing campaign keywords
      event_footprint    20  – number of known events
      competitor_pressure 20 – competitor recent activity volume
      contact_quality    20  – named decision-makers with emails
      base               10  – always present
      risk_penalty       -20 – news titles containing risk keywords
    """
    # Base
    base = 10

    # Campaign activity in news (up to 30 pts)
    campaign_hits = sum(
        1 for n in news
        if _CAMPAIGN_KEYWORDS.search(n.get("title", "") + " " + (n.get("summary") or ""))
    )
    campaign_score = min(campaign_hits * 6, 30)

    # Event footprint (up to 20 pts)
    event_score = min(len(events) * 4, 20)

    # Competitor pressure (up to 20 pts)
    comp_activity_count = sum(
        len(c.get("recent_activity", [])) for c in competitors
    )
    competitor_score = min(comp_activity_count * 3, 20)

    # Contact quality (up to 20 pts)
    named_contacts = sum(
        1 for c in contacts
        if c.get("name") and (c.get("email_guesses") or c.get("linkedin_url"))
    )
    contact_score = min(named_contacts * 7, 20)

    # Risk penalty (up to -20 pts)
    risk_hits = sum(
        1 for n in news
        if _RISK_KEYWORDS.search(n.get("title", "") + " " + (n.get("summary") or ""))
    )
    risk_penalty = -min(risk_hits * 5, 20)

    return {
        "base":               base,
        "campaign_activity":  campaign_score,
        "event_footprint":    event_score,
        "competitor_pressure": competitor_score,
        "contact_quality":    contact_score,
        "risk_penalty":       risk_penalty,
    }
