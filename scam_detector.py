SCAM_KEYWORDS = [
    "fraud", "scam", "ponzi", "fake", "manipulation",
    "insider trading", "money laundering", "illegal",
    "accounting irregularities"
]


def get_scam_score(text):
    text = text.lower()

    hits = sum(1 for word in SCAM_KEYWORDS if word in text)

    score = min(hits / 3, 1.0)

    return round(score, 3)