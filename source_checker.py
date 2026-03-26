SOURCE_TRUST = {
    "reuters": 0.95,
    "bloomberg": 0.95,
    "cnbc": 0.85,
    "economic times": 0.80,
    "moneycontrol": 0.75,
    "twitter": 0.30,
    "x.com": 0.30,
    "reddit": 0.35,
    "whatsapp": 0.20,
    "unknown": 0.40
}


def get_source_trust(text: str) -> float:
    text = (text or "").lower()

    for source, score in SOURCE_TRUST.items():
        if source in text:
            return score

    return SOURCE_TRUST["unknown"]