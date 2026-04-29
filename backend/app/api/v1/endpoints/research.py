"""
research.py – FastAPI router for the /research endpoint.

POST /api/v1/research
    Body: { "company_name": "Stripe", "category": "online payment processing" }
    Returns: raw data schema (see research_orchestrator.collect_raw_data)

The response is also saved to data/raw/<company_name>.json for offline use
by Persons B and C.
"""

import json
import logging
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.research_orchestrator import collect_raw_data

logger = logging.getLogger(__name__)
router = APIRouter(tags=["research"])

# Directory where raw JSON files are saved
_DATA_DIR = Path(__file__).resolve().parents[5] / "data" / "raw"


class ResearchRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200, examples=["Stripe"])
    category: str = Field(
        default="",
        max_length=200,
        examples=["online payment processing"],
    )


class ResearchResponse(BaseModel):
    company_name: str
    category: str
    website: str
    overview: dict
    market_perception: dict
    competitors: list
    brand_activity: list
    events: list
    decision_makers_raw: list
    contacts_raw: list
    _errors: dict = {}


@router.post("/research", summary="Collect raw company data")
async def research_endpoint(request: ResearchRequest) -> dict:
    """
    Trigger the full data-collection pipeline for a company.

    - Finds the company website
    - Scrapes about-page content and scale indicators
    - Fetches recent news headlines
    - Discovers up to 5 competitors with recent activity
    - Finds brand events and activations
    - Identifies marketing/brand decision-makers
    - Enriches contacts with guessed emails and LinkedIn URLs

    The result is returned as JSON **and** saved to `data/raw/<company_name>.json`.
    """
    logger.info("Research request: company='%s' category='%s'", request.company_name, request.category)

    try:
        data = await collect_raw_data(request.company_name, request.category)
    except Exception as exc:
        logger.exception("Orchestrator failed for '%s'", request.company_name)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Persist to disk for offline analysis
    _save_to_disk(request.company_name, data)

    return data


def _save_to_disk(company_name: str, data: dict) -> None:
    """Write the raw data dict to data/raw/<company_name>.json."""
    try:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in company_name)
        file_path = _DATA_DIR / f"raw_{safe_name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        logger.info("Saved raw data to %s", file_path)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not save raw data to disk: %s", exc)
