RUMOR_KEYWORDS = [
    "rumor",
    "unconfirmed",
    "sources say",
    "allegedly",
    "reportedly",
    "speculation",
    "claims",
    "viral",
    "leak",
    "insiders say",
    "may be",
    "might",
    "possibly",
    "suggests",
    "suggesting"
]


def get_rumor_score(text: str) -> float:
    text = (text or "").lower()
    count = sum(1 for word in RUMOR_KEYWORDS if word in text)
    return round(min(count / 5, 1.0), 4)