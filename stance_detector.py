STANCE_LABELS = [
    "confirmed factual statement",
    "speculative statement",
    "rumor or unverified claim",
    "opinion"
]


def detect_stance(text: str, stance_clf) -> dict:
    result = stance_clf(text, STANCE_LABELS)

    label = result["labels"][0]
    score = float(result["scores"][0])

    if "rumor" in label:
        risk = 1.0
    elif "speculative" in label:
        risk = 0.7
    elif "opinion" in label:
        risk = 0.5
    else:
        risk = 0.2

    return {
        "stance": label,
        "stance_score": round(score, 4),
        "stance_risk": round(risk, 4)
    }