"""
company.py – Brand intelligence endpoints (main API for Person 2 & 3).

POST /api/v1/company/analyze          – raw scrape pipeline
POST /api/v1/company/full_intel       – raw + LLM enrichment (main hackathon endpoint)
GET  /api/v1/company/overview/{name}  – overview section only
GET  /api/v1/company/competitors/{name}
GET  /api/v1/company/people/{name}
GET  /api/v1/company/news/{name}
GET  /api/v1/company/events/{name}
"""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from ...core.config import settings
from ...services.enrich_processor import enrich_raw_data
from ...services.orchestrator import collect_raw_data

logger = logging.getLogger(__name__)
router = APIRouter(tags=["company"])


class CompanyRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200, examples=["Stripe"])
    category: str = Field(default="", max_length=200, examples=["online payment processing"])


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

@router.post("/company/analyze", summary="Full brand intelligence pipeline")
async def analyze_company(
    request: CompanyRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Run all scrapers and return the unified raw-data schema.

    Guaranteed fields (may be empty string / empty list, never fabricated):
      - company_name, category, website, domain
      - overview.about_text
      - market_perception.recent_news_headlines
      - competitors (list, may be empty)
      - brand_activity (list, may be empty)
      - events (list, may be empty)

    Nullable fields (return null if not found):
      - overview.scale_indicators.revenue / employees / founded
      - contacts_raw[].email
      - decision_makers_raw[].name
    """
    try:
        raw = await collect_raw_data(request.company_name, request.category)
    except Exception as exc:
        logger.exception("Pipeline failed for '%s'", request.company_name)
        raise HTTPException(status_code=500, detail=f"Data collection failed: {exc}") from exc

    background_tasks.add_task(_save_raw, request.company_name, raw)
    return raw


# ---------------------------------------------------------------------------
# Full intelligence (raw + LLM enrichment) – PRIMARY HACKATHON ENDPOINT
# ---------------------------------------------------------------------------

@router.post("/company/full_intel", summary="Full brand intelligence with LLM insights")
async def full_intelligence(
    request: CompanyRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Run the complete pipeline: scrape → enrich with LLM → return all 10 outputs.

    This is the primary endpoint for Person 3's frontend.

    Output fields mapping to hackathon requirements:
      #1  company_overview        – LLM summary of about page
      #2  market_position         – LLM analysis of news sentiment
      #3  competitor_mapping      – [{name, strength, gap}]
      #4  brand_activity_summary  – top 10 news items
      #5  event_footprint         – events list
      #6  strategic_watchouts     – 3 risk bullets
      #7  decision_makers         – contacts with linkedin_message, email_subject, email_body
      #8  opportunity_score       – 0-100 integer
      #9  outreach_generated      – bool confirming messages were created
      #10 _llm_backend            – which LLM was used
    """
    try:
        raw = await collect_raw_data(request.company_name, request.category)
        enriched = await enrich_raw_data(raw)
    except Exception as exc:
        logger.exception("full_intel failed for '%s'", request.company_name)
        raise HTTPException(status_code=500, detail=f"Intelligence pipeline failed: {exc}") from exc

    background_tasks.add_task(_save_raw,      request.company_name, raw)
    background_tasks.add_task(_save_enriched, request.company_name, enriched)
    return enriched


# ---------------------------------------------------------------------------
# Granular endpoints (load from cache file if available, else re-collect)
# ---------------------------------------------------------------------------

@router.get("/company/overview/{company_name}", summary="Company overview only")
async def get_overview(company_name: str) -> dict:
    raw = await _load_or_collect(company_name)
    return raw.get("overview", {})


@router.get("/company/competitors/{company_name}", summary="Competitor list")
async def get_competitors(company_name: str) -> list:
    raw = await _load_or_collect(company_name)
    return raw.get("competitors", [])


@router.get("/company/people/{company_name}", summary="Decision-makers and contacts")
async def get_people(company_name: str) -> dict:
    raw = await _load_or_collect(company_name)
    return {
        "decision_makers": raw.get("decision_makers_raw", []),
        "contacts": raw.get("contacts_raw", []),
    }


@router.get("/company/news/{company_name}", summary="Recent news and brand activity")
async def get_news(company_name: str) -> list:
    raw = await _load_or_collect(company_name)
    return raw.get("brand_activity", [])


@router.get("/company/events/{company_name}", summary="Events and activations")
async def get_events(company_name: str) -> list:
    raw = await _load_or_collect(company_name)
    return raw.get("events", [])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _load_or_collect(company_name: str) -> dict:
    """Return cached JSON if available, otherwise run the full pipeline."""
    cached = _load_cached(company_name)
    if cached:
        return cached
    return await collect_raw_data(company_name, "")


def _load_cached(company_name: str) -> dict | None:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in company_name)
    path = settings.DATA_DIR / f"{safe}.json"
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.warning("Could not read cache for '%s': %s", company_name, exc)
    return None


def _save_raw(company_name: str, data: dict) -> None:
    _save_json(settings.DATA_DIR, company_name, data)


def _save_enriched(company_name: str, data: dict) -> None:
    enriched_dir = settings.DATA_DIR.parent / "enriched"
    _save_json(enriched_dir, company_name, data)


def _save_json(directory: Path, company_name: str, data: dict) -> None:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in company_name)
        path = directory / f"{safe}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        logger.info("Saved → %s", path)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not save JSON for '%s': %s", company_name, exc)
