"""
tracking_service.py – Email open/click tracking via pixel and redirect links.

Uses SQLite (no extra infra needed for hackathon demo).
Tables:
  email_events  – one row per open or click event
  click_links   – maps a short link_id to the real target URL
"""

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.config import settings

DB_PATH: str = settings.TRACKING_DB

# 1×1 transparent GIF
_PIXEL_BYTES = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00"
    b"!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01"
    b"\x00\x00\x02\x02D\x01\x00;"
)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init_tracking_db() -> None:
    """Create tables if they don't exist. Safe to call on every startup."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS email_events (
            id           TEXT PRIMARY KEY,
            recipient    TEXT,
            company_name TEXT,
            event_type   TEXT,
            timestamp    TEXT,
            user_agent   TEXT,
            ip           TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS click_links (
            id         TEXT PRIMARY KEY,
            target_url TEXT NOT NULL,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Pixel generation
# ---------------------------------------------------------------------------

def generate_pixel_url(recipient: str, company: str) -> str:
    """
    Return a tracking pixel URL for embedding in an email.

    The URL encodes a unique event_id so each send is individually tracked.
    """
    event_id = str(uuid.uuid4())
    return (
        f"{settings.BASE_URL}/api/v1/tracking/pixel/{event_id}"
        f"?recipient={recipient}&company={company}"
    )


def pixel_bytes() -> bytes:
    """Return the raw bytes of a 1×1 transparent GIF."""
    return _PIXEL_BYTES


# ---------------------------------------------------------------------------
# Click-link generation
# ---------------------------------------------------------------------------

def generate_tracked_link(target_url: str) -> str:
    """
    Store a target URL and return a short redirect URL.
    Embed this in emails instead of the raw link.
    """
    link_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO click_links (id, target_url, created_at) VALUES (?, ?, ?)",
        (link_id, target_url, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return f"{settings.BASE_URL}/api/v1/tracking/click/{link_id}"


def resolve_click_link(link_id: str) -> Optional[str]:
    """Return the target URL for a given link_id, or None if not found."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT target_url FROM click_links WHERE id = ?", (link_id,)
    ).fetchone()
    conn.close()
    return row[0] if row else None


# ---------------------------------------------------------------------------
# Event logging
# ---------------------------------------------------------------------------

def log_event(
    event_id: str,
    recipient: str,
    company: str,
    event_type: str,
    user_agent: str = "",
    ip: str = "",
) -> None:
    """Persist an open or click event to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT OR IGNORE INTO email_events
           (id, recipient, company_name, event_type, timestamp, user_agent, ip)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            event_id,
            recipient,
            company,
            event_type,
            datetime.utcnow().isoformat(),
            user_agent,
            ip,
        ),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def get_events(company: Optional[str] = None, recipient: Optional[str] = None) -> list:
    """Return logged events, optionally filtered by company or recipient."""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT id, recipient, company_name, event_type, timestamp, user_agent, ip FROM email_events"
    params: list = []
    conditions: list[str] = []
    if company:
        conditions.append("company_name = ?")
        params.append(company)
    if recipient:
        conditions.append("recipient = ?")
        params.append(recipient)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY timestamp DESC LIMIT 500"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [
        {
            "id": r[0], "recipient": r[1], "company": r[2],
            "event_type": r[3], "timestamp": r[4],
            "user_agent": r[5], "ip": r[6],
        }
        for r in rows
    ]
