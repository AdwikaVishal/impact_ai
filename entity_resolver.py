ENTITY_ALIASES = {
    "rbi": "Reserve Bank of India",
    "sebi": "Securities and Exchange Board of India",
    "tcs": "Tata Consultancy Services",
    "sbi": "State Bank of India",
    "icici": "ICICI Bank",
    "hdfc": "HDFC Bank",
    "dominos": "Domino's Pizza",
    "domino's": "Domino's Pizza",
    "google": "Alphabet",
    "facebook": "Meta"
}


def normalize_entity(raw_name: str) -> dict:
    if not raw_name:
        return {
            "display_name": "Unknown",
            "market_entity": "Unknown"
        }

    cleaned = raw_name.strip()
    lowered = cleaned.lower()

    display_name = ENTITY_ALIASES.get(lowered, cleaned)

    return {
        "display_name": display_name,
        "market_entity": display_name
    }