CANDIDATE_EVENTS = [
    "fraud",
    "earnings",
    "regulation",
    "policy",
    "rumor",
    "analyst downgrade",
    "bankruptcy",
    "liquidity crisis",
    "investigation",
    "lawsuit"
]


def classify_event(text: str, event_clf) -> dict:
    result = event_clf(text, CANDIDATE_EVENTS)
    return {
        "event": result["labels"][0],
        "event_score": round(float(result["scores"][0]), 4)
    }