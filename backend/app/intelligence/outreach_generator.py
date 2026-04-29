"""
outreach_generator.py – Generates Output #9 (Personalised LinkedIn messages & email drafts)
"""

import logging

from .llm_client import get_llm
from .prompts import EMAIL_PROMPT, LINKEDIN_PROMPT

logger = logging.getLogger(__name__)

_LINKEDIN_LIMIT = 300


async def generate_linkedin_message(
    contact: dict,
    company_name: str,
    recent_activity: list,
) -> str:
    """Generate a personalised LinkedIn connection message (≤ 300 chars)."""
    name = contact.get("name") or "there"
    if name in ("Unknown", ""):
        name = "there"
    role = contact.get("role") or "marketing professional"

    activity_text = "\n".join(
        f"• {a.get('title', '')[:80]}"
        for a in recent_activity[:3]
        if a.get("title")
    ) or f"recent brand initiatives at {company_name}"

    prompt = LINKEDIN_PROMPT.format(
        name=name,
        role=role,
        company_name=company_name,
        activity_summary=activity_text,
    )
    message = await get_llm().generate(prompt, max_tokens=200)
    message = message.strip().strip('"').strip("'")

    if len(message) > _LINKEDIN_LIMIT:
        message = message[:_LINKEDIN_LIMIT - 1].rsplit(" ", 1)[0] + "…"

    logger.info("[outreach] LinkedIn for %s @ %s (%d chars)", name, company_name, len(message))
    return message or f"Hi {name}, noticed your great work at {company_name}. Would love to connect."


async def generate_email(
    contact: dict,
    company_name: str,
    recent_activity: list,
) -> dict:
    """Generate a personalised email with subject line and body."""
    name = contact.get("name") or "Team"
    if name in ("Unknown", ""):
        name = "Team"
    role = contact.get("role") or "marketing team"

    activity_text = "\n".join(
        f"• {a.get('title', '')[:100]}"
        for a in recent_activity[:3]
        if a.get("title")
    ) or f"your recent brand momentum at {company_name}"

    prompt = EMAIL_PROMPT.format(
        name=name,
        role=role,
        company_name=company_name,
        activity_summary=activity_text,
    )
    response = await get_llm().generate(prompt, max_tokens=450)

    # Parse subject / body
    subject = f"Thoughts on {company_name}'s brand strategy"
    body = response.strip()

    if "Subject:" in response:
        lines = response.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("Subject:"):
                subject = line.replace("Subject:", "").strip()
                body = "\n".join(lines[i + 1:]).strip()
                # Strip leading "Body:" label if present
                if body.lower().startswith("body:"):
                    body = body[5:].strip()
                break

    logger.info("[outreach] Email for %s @ %s – subject: '%s'", name, company_name, subject[:60])
    return {"subject": subject, "body": body}
