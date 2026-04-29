"""
config.py – Centralised environment variable loading.

All secrets and tuneable values live here. Import `settings` anywhere.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the backend/ directory (one level above app/)
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_ENV_PATH)


class Settings:
    # ── API keys (all optional – scrapers degrade gracefully without them) ──
    NEWS_API_KEY:      str | None = os.getenv("NEWS_API_KEY")
    NEWSDATA_API_KEY:  str | None = os.getenv("NEWSDATA_API_KEY")
    SERPER_KEY:        str | None = os.getenv("SERPER_KEY")
    HUNTER_API_KEY:    str | None = os.getenv("HUNTER_API_KEY")
    OPENAI_API_KEY:    str | None = os.getenv("OPENAI_API_KEY")

    # ── LLM ──────────────────────────────────────────────────────────────────
    OPENAI_API_KEY:  str | None = os.getenv("OPENAI_API_KEY")
    OLLAMA_BASE_URL: str        = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    MODEL_NAME:      str        = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    # ── Tracking ─────────────────────────────────────────────────────────────
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    # ── Paths ─────────────────────────────────────────────────────────────────
    DATA_DIR:      Path = Path(os.getenv("DATA_DIR", "data/raw"))
    ENRICHED_DIR:  Path = Path(os.getenv("ENRICHED_DIR", "data/enriched"))
    TRACKING_DB:   str  = os.getenv("TRACKING_DB", "tracking.db")

    # ── Cache ─────────────────────────────────────────────────────────────────
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # seconds


settings = Settings()
