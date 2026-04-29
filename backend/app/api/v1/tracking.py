"""
tracking.py – Email open/click tracking endpoints.

GET /api/v1/tracking/pixel/{event_id}   – 1×1 GIF, logs an "open" event
GET /api/v1/tracking/click/{link_id}    – redirects to target URL, logs a "click"
GET /api/v1/tracking/events             – query logged events (for Person 3 dashboard)
POST /api/v1/tracking/link              – generate a tracked redirect link
"""

import logging

from fastapi import APIRouter, Query, Request, Response
from pydantic import BaseModel

from ...services.tracking_service import (
    generate_tracked_link,
    get_events,
    log_event,
    pixel_bytes,
    resolve_click_link,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["tracking"])


# ---------------------------------------------------------------------------
# Pixel endpoint – email open tracking
# ---------------------------------------------------------------------------

@router.get(
    "/tracking/pixel/{event_id}",
    summary="Email open tracking pixel",
    response_class=Response,
)
async def tracking_pixel(
    event_id: str,
    request: Request,
    recipient: str = Query(default=""),
    company: str = Query(default=""),
) -> Response:
    """
    Return a 1×1 transparent GIF and log an 'open' event.
    Embed the URL returned by `generate_pixel_url()` as an `<img>` tag in emails.
    """
    log_event(
        event_id=event_id,
        recipient=recipient,
        company=company,
        event_type="open",
        user_agent=request.headers.get("user-agent", ""),
        ip=request.client.host if request.client else "",
    )
    logger.info("Open tracked: recipient=%s company=%s", recipient, company)
    return Response(content=pixel_bytes(), media_type="image/gif")


# ---------------------------------------------------------------------------
# Click redirect endpoint
# ---------------------------------------------------------------------------

@router.get(
    "/tracking/click/{link_id}",
    summary="Tracked link redirect",
)
async def tracking_click(link_id: str, request: Request) -> Response:
    """
    Log a 'click' event and redirect to the original target URL.
    """
    target = resolve_click_link(link_id)
    if not target:
        return Response("Link not found", status_code=404)

    log_event(
        event_id=link_id,
        recipient="",
        company="",
        event_type="click",
        user_agent=request.headers.get("user-agent", ""),
        ip=request.client.host if request.client else "",
    )
    logger.info("Click tracked: link_id=%s → %s", link_id, target)
    return Response(status_code=302, headers={"Location": target})


# ---------------------------------------------------------------------------
# Generate a tracked link
# ---------------------------------------------------------------------------

class LinkRequest(BaseModel):
    target_url: str


@router.post("/tracking/link", summary="Generate a tracked redirect link")
async def create_tracked_link(body: LinkRequest) -> dict:
    """
    Store a target URL and return a short tracked redirect URL.
    Use this when building outreach emails.
    """
    tracked = generate_tracked_link(body.target_url)
    return {"tracked_url": tracked, "original_url": body.target_url}


# ---------------------------------------------------------------------------
# Query logged events (for Person 3 dashboard)
# ---------------------------------------------------------------------------

@router.get("/tracking/events", summary="Query email tracking events")
async def query_events(
    company: str = Query(default=""),
    recipient: str = Query(default=""),
) -> list:
    """
    Return logged open/click events.
    Filter by `company` or `recipient` query params.
    """
    return get_events(
        company=company or None,
        recipient=recipient or None,
    )
