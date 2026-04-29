"""
main.py – Impact AI backend entry point.

Routers:
  /api/v1/company/*   – brand intelligence pipeline (Person 2 & 3)
  /api/v1/tracking/*  – email open/click tracking
  /api/v1/research    – legacy single-endpoint alias (kept for compatibility)

Start with:
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.company import router as company_router
from app.api.v1.tracking import router as tracking_router
from app.api.v1.endpoints.research import router as research_router  # legacy alias
from app.services.tracking_service import init_tracking_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s – %(message)s",
)

app = FastAPI(
    title="Impact AI – Brand Intelligence Engine",
    version="3.0.0",
    description=(
        "Data collection, brand research, and outreach automation API. "
        "See /docs for interactive documentation."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_tracking_db()


# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(company_router,  prefix="/api/v1")
app.include_router(tracking_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")   # legacy: POST /api/v1/research


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "healthy", "service": "Impact AI – Brand Intelligence Engine"}
