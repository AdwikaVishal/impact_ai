"""
enricher.py – Main enrichment pipeline.

Takes raw scraped data and produces the complete 10-output structure
using Groq LLM for intelligence generation.
"""

import asyncio
import logging

from .activity_summarizer import summarize_brand_activity, summarize_events
from .competitor_analyzer import analyze_competitors
from .outreach_generator import generate_email, generate_linkedin_message
from .overview_generator import generate_company_overview, generate_market_position
from .watchout_generator import generate_watchouts

logger = logging.getLogger(__name__)


async def enrich_company_data(raw_data: dict) -> dict:
    """
    Takes raw data from the scraping pipeline and returns enriched intelligence
    with all 10 required outputs.
    """
    company_name = raw_data.get("company_name", "Unknown")
    category = raw_data.get("category", "")
    about_text = raw_data.get("overview", {}).get("about_text", "")
    news = raw_data.get("brand_activity", [])
    competitors = raw_data.get("competitors", [])
    events = raw_data.get("events", [])
    contacts = raw_data.get("contacts_raw", [])

    logger.info("🧠 Enriching data for %s...", company_name)

    # Run all independent LLM tasks concurrently
    (
        overview,
        market_position,
        competitor_analysis,
        watchouts,
        brand_activity_summary,
        events_summary,
    ) = await asyncio.gather(
        generate_company_overview(about_text),
        generate_market_position(company_name, news),
        analyze_competitors(company_name, category, competitors),
        generate_watchouts(company_name, news, competitors, events),
        summarize_brand_activity(news),
        summarize_events(events),
    )

    # Generate personalised outreach for each contact (sequential to avoid rate limits)
    enriched_contacts = []
    for contact in contacts:
        try:
            linkedin_msg, email = await asyncio.gather(
                generate_linkedin_message(contact, company_name, news),
                generate_email(contact, company_name, news),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Outreach generation failed for %s: %s", contact.get("name"), exc)
            linkedin_msg = ""
            email = {"subject": "", "body": ""}

        enriched_contacts.append({
            "name":             contact.get("name") or "Unknown",
            "role":             contact.get("role") or "Marketing Professional",
            "email":            (contact.get("email_guesses") or ["Not available"])[0],
            "email_guesses":    contact.get("email_guesses", []),
            "linkedin_url":     contact.get("linkedin_url") or "Not available",
            "confidence":       contact.get("confidence", "low"),
            "linkedin_message": linkedin_msg,
            "email_subject":    email.get("subject", ""),
            "email_body":       email.get("body", ""),
        })

    enriched_data = {
        # Output #1 – Company Overview
        "company_overview": overview,

        # Output #2 – Market Position
        "market_position": market_position,

        # Output #3 – Competitor Mapping
        "competitor_mapping": competitor_analysis,

        # Output #4 – Brand Activity
        "brand_activity": {
            "summary":       brand_activity_summary.get("summary", ""),
            "recent_count":  brand_activity_summary.get("recent_count", 0),
            "campaigns":     brand_activity_summary.get("campaigns", []),
            "launches":      brand_activity_summary.get("launches", []),
            "announcements": brand_activity_summary.get("announcements", []),
            "recent_items":  brand_activity_summary.get("recent_items", []),
        },

        # Output #5 – Events Footprint
        "events_footprint": {
            "summary":     events_summary.get("summary", ""),
            "total":       events_summary.get("total", 0),
            "conferences": events_summary.get("conferences", 0),
            "webinars":    events_summary.get("webinars", 0),
            "activations": events_summary.get("activations", 0),
            "events":      events_summary.get("events", []),
        },

        # Output #6 – Strategic Watchouts
        "strategic_watchouts": watchouts,

        # Outputs #7, #8, #9 – Decision Makers with Contact Intelligence & Outreach
        "decision_makers": enriched_contacts,

        # Output #10 – Tracking (handled by tracking service)
        "tracking": {
            "status":  "ready",
            "message": "Tracking system active – use /api/v1/tracking endpoints",
        },

        # Pass-through raw fields for frontend use
        "company_name":  company_name,
        "category":      category,
        "website":       raw_data.get("website", ""),
        "domain":        raw_data.get("domain"),
        "raw_overview":  raw_data.get("overview", {}),
        "outreach_generated": bool(enriched_contacts),
        "_llm_backend":  "groq",
        "enriched_at":   "groq_llm_generated",
    }

    logger.info("✅ Enrichment complete for %s", company_name)
    return enriched_data
