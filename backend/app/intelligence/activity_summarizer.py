"""
activity_summarizer.py – Generates Output #4 (Brand Activity) and Output #5 (Events Footprint)
"""

from datetime import datetime, timedelta


async def summarize_brand_activity(brand_activity: list, months_back: int = 24) -> dict:
    """Output #4: Brand Activity (last 12-24 months)"""

    if not brand_activity:
        return {
            "total": 0,
            "recent_count": 0,
            "recent_items": [],
            "campaigns": [],
            "launches": [],
            "announcements": [],
            "summary": "No brand activity found in the last 24 months.",
        }

    cutoff_date = datetime.now() - timedelta(days=months_back * 30)
    recent_items = []

    for item in brand_activity:
        date_str = item.get("date", "")
        if date_str:
            try:
                item_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                if item_date >= cutoff_date:
                    recent_items.append(item)
            except (ValueError, TypeError):
                recent_items.append(item)
        else:
            recent_items.append(item)

    campaigns, launches, announcements = [], [], []
    for item in recent_items[:15]:
        title = item.get("title", "").lower()
        if any(w in title for w in ["launch", "release", "introduc", "unveil"]):
            launches.append(item)
        elif any(w in title for w in ["campaign", "advertising", "marketing", "sponsor"]):
            campaigns.append(item)
        else:
            announcements.append(item)

    return {
        "total": len(brand_activity),
        "recent_count": len(recent_items),
        "recent_items": recent_items[:10],
        "campaigns": campaigns[:3],
        "launches": launches[:3],
        "announcements": announcements[:3],
        "summary": (
            f"Found {len(recent_items)} brand activities in the last {months_back} months, "
            f"including {len(launches)} product launches and {len(campaigns)} marketing campaigns."
        ),
    }


async def summarize_events(events: list) -> dict:
    """Output #5: Events Footprint"""

    if not events:
        return {
            "total": 0,
            "events": [],
            "conferences": 0,
            "webinars": 0,
            "activations": 0,
            "summary": "No events found for this company.",
        }

    conferences, webinars, activations = 0, 0, 0
    for event in events:
        url = (event.get("source_url") or "").lower()
        snippet = (event.get("snippet") or "").lower()
        combined = url + " " + snippet
        if any(w in combined for w in ["conference", "summit", "expo", "trade show"]):
            conferences += 1
        elif any(w in combined for w in ["webinar", "virtual", "online event"]):
            webinars += 1
        else:
            activations += 1

    return {
        "total": len(events),
        "events": events[:5],
        "conferences": conferences,
        "webinars": webinars,
        "activations": activations,
        "summary": (
            f"Identified {len(events)} events, including {conferences} conferences/summits "
            f"and {activations} brand activations."
        ),
    }
