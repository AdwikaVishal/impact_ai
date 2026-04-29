"""
contact_scraper.py – Enrich decision-maker records with guessed emails and LinkedIn URLs.

NOTE: Email addresses produced here are *guesses* based on common patterns
(first.last@domain). Person B should verify them before outreach.

Main export:
  - enrich_contacts(decision_makers, domain) -> list[dict]
"""

import asyncio
import logging
import re

from googlesearch import search

logger = logging.getLogger(__name__)

# Common corporate email patterns (ordered by prevalence)
_EMAIL_PATTERNS = [
    "{first}.{last}",
    "{first}{last}",
    "{first}",
    "{first[0]}{last}",
    "{first[0]}.{last}",
]


async def enrich_contacts(decision_makers: list, domain: str) -> list:
    """
    Add guessed email addresses and LinkedIn URLs to each decision-maker record.

    Args:
        decision_makers: Output of find_decision_makers().
        domain:          Company domain (e.g. "stripe.com").

    Returns:
        List of enriched contact dicts:
        {
            "name":          str | None,
            "role":          str | None,
            "email_guesses": list[str],   # ordered by likelihood
            "linkedin_url":  str | None,
            "source":        str,
        }
    """
    tasks = [_enrich_one(dm, domain) for dm in decision_makers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    contacts = []
    for dm, result in zip(decision_makers, results):
        if isinstance(result, dict):
            contacts.append(result)
        else:
            # Return a minimal record on error
            contacts.append(
                {
                    "name": dm.get("name"),
                    "role": dm.get("role"),
                    "email_guesses": [],
                    "linkedin_url": dm.get("source_url") if "linkedin" in (dm.get("source_url") or "") else None,
                    "source": dm.get("source", "unknown"),
                }
            )

    logger.info("Enriched %d contacts for domain '%s'", len(contacts), domain)
    return contacts


async def _enrich_one(dm: dict, domain: str) -> dict:
    name: str = dm.get("name") or ""
    role: str = dm.get("role") or ""
    existing_linkedin = dm.get("source_url") if "linkedin" in (dm.get("source_url") or "") else None

    email_guesses = _generate_email_guesses(name, domain)

    # Only search LinkedIn if we don't already have a URL
    linkedin_url = existing_linkedin
    if not linkedin_url and name:
        linkedin_url = await _find_linkedin_url(name, domain)

    return {
        "name": name or None,
        "role": role or None,
        "email_guesses": email_guesses,
        "linkedin_url": linkedin_url,
        "source": dm.get("source", "unknown"),
    }


def _generate_email_guesses(name: str, domain: str) -> list:
    """
    Generate plausible email addresses for a person at a given domain.

    Returns an empty list if the name cannot be parsed into first/last.
    """
    if not name or not domain:
        return []

    parts = name.lower().split()
    if len(parts) < 2:
        return [f"{parts[0]}@{domain}"] if parts else []

    first = _sanitize(parts[0])
    last = _sanitize(parts[-1])

    guesses = []
    for pattern in _EMAIL_PATTERNS:
        try:
            local = pattern.format(
                first=first,
                last=last,
                **{f"first[{i}]": first[i] for i in range(min(3, len(first)))},
            )
            email = f"{local}@{domain}"
            if email not in guesses:
                guesses.append(email)
        except (IndexError, KeyError):
            continue

    return guesses


async def _find_linkedin_url(name: str, company_hint: str) -> str:
    """Search Google for a LinkedIn profile URL."""
    query = f'site:linkedin.com/in "{name}" "{company_hint}"'
    try:
        for url in search(query, num_results=2, sleep_interval=1):
            if "linkedin.com/in/" in url:
                return url
    except Exception as exc:  # noqa: BLE001
        logger.warning("LinkedIn search failed for '%s': %s", name, exc)
    return ""


def _sanitize(s: str) -> str:
    """Remove non-alpha characters (hyphens, apostrophes, etc.)."""
    return re.sub(r"[^a-z]", "", s.lower())
