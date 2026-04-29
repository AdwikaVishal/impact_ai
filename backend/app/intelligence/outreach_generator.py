"""
outreach_generator.py – Generate personalised LinkedIn messages and email drafts.

Exports:
  - generate_linkedin_message(decision_maker, company_name, recent_activity, opportunity_angle) -> str
  - generate_email(decision_maker, company_name, recent_activity, opportunity_angle)            -> dict
  - generate_opportunity_angle(company_name, activity_summary)                                  -> str
"""

import logging
import re

from .llm_client import get_llm
from .prompts import EMAIL_DRAFT_PROMPT, LINKEDIN_MESSAGE_PROMPT, OPPORTUNITY_ANGLE_PROMPT

logger = logging.getLogger(__name__)

_LINKEDIN_CHAR_LIMIT = 300   # LinkedIn connection message limit
_DEFAULT_ANGLE = "helping brands amplify their marketing impact through strategic partnerships"


async def generate_opportunity_angle(company_name: str, activity_summary: str) -> str:
    """
    Derive a one-sentence opportunity angle from recent brand activity.
    Used as context for both LinkedIn and email generation.
    """
    if not activity_summary:
        return _DEFAULT_ANGLE

    prompt = OPPORTUNITY_ANGLE_PROMPT.format(
        company_name=company_name,
        activity_summary=activity_summary[:500],
    )
    result = await get_llm().generate(prompt, max_tokens=60)
    return result.strip() or _DEFAULT_ANGLE


async def generate_linkedin_message(
    decision_maker: dict,
    company_name: str,
    recent_activity: list,
    opportunity_angle: str = "",
) -> str:
    """
    Generate a short LinkedIn connection message personalised to the decision-maker.

    Returns a string of ≤ 300 characters.
    """
    name = decision_maker.get("name") or "there"
    role = decision_maker.get("role") or "Marketing leader"
    activity_summary = _summarise_activity(recent_activity)

    if not opportunity_angle:
        opportunity_angle = await generate_opportunity_angle(company_name, activity_summary)

    prompt = LINKEDIN_MESSAGE_PROMPT.format(
        decision_maker_name=name,
        role=role,
        company_name=company_name,
        recent_activity_summary=activity_summary,
        opportunity_angle=opportunity_angle,
    )

    msg = await get_llm().generate(prompt, max_tokens=200)
    msg = msg.strip().strip('"').strip("'")   # remove any surrounding quotes

    # Hard-trim to LinkedIn's limit
    if len(msg) > _LINKEDIN_CHAR_LIMIT:
        msg = msg[:_LINKEDIN_CHAR_LIMIT - 1].rsplit(" ", 1)[0] + "…"

    logger.info(
        "[outreach] LinkedIn message for %s @ %s (%d chars)",
        name, company_name, len(msg),
    )
    return msg


async def generate_email(
    decision_maker: dict,
    company_name: str,
    recent_activity: list,
    opportunity_angle: str = "",
) -> dict:
    """
    Generate a full email draft with subject line and body.

    Returns:
        {
            "subject": str,
            "body":    str,
        }
    """
    name = decision_maker.get("name") or "there"
    role = decision_maker.get("role") or "Marketing leader"
    activity_summary = _summarise_activity(recent_activity)

    if not opportunity_angle:
        opportunity_angle = await generate_opportunity_angle(company_name, activity_summary)

    prompt = EMAIL_DRAFT_PROMPT.format(
        decision_maker_name=name,
        role=role,
        company_name=company_name,
        recent_activity_summary=activity_summary,
        opportunity_angle=opportunity_angle,
    )

    response = await get_llm().generate(prompt, max_tokens=450)
    parsed = _parse_email(response)

    logger.info(
        "[outreach] Email for %s @ %s – subject: '%s'",
        name, company_name, parsed["subject"][:60],
    )
    return parsed


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _summarise_activity(recent_activity: list) -> str:
    """Turn a list of news/activity dicts into a short comma-separated string."""
    titles = [
        a.get("title") or a.get("snippet") or str(a)
        for a in recent_activity[:4]
        if a
    ]
    return ", ".join(t for t in titles if t) or "recent brand initiatives"


def _parse_email(response: str) -> dict:
    """
    Extract subject and body from the LLM response.

    Expected format:
        Subject: <subject line>
        Body:
        <body text>
    """
    subject = ""
    body = response.strip()

    # Extract subject line
    subject_match = re.search(r"(?i)^subject:\s*(.+)$", response, re.MULTILINE)
    if subject_match:
        subject = subject_match.group(1).strip()

    # Extract body (everything after "Body:" or after the subject line)
    body_match = re.search(r"(?i)^body:\s*\n?(.*)", response, re.DOTALL | re.MULTILINE)
    if body_match:
        body = body_match.group(1).strip()
    elif subject:
        # Remove the subject line and use the rest as body
        body = re.sub(r"(?i)^subject:.*\n?", "", response, count=1).strip()

    return {
        "subject": subject or "Thoughts on your recent brand activity",
        "body":    body or response.strip(),
    }
