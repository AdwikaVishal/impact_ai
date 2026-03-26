ENTITY_MAP = {
    "rbi": "Reserve Bank of India",
    "sebi": "Securities and Exchange Board of India",
    "tcs": "Tata Consultancy Services",
    "sbi": "State Bank of India",
    "icici": "ICICI Bank",
    "hdfc": "HDFC Bank",
    "infosys": "Infosys",
    "reliance": "Reliance Industries",
    "adani": "Adani Enterprises",
    "wipro": "Wipro",
    "axis": "Axis Bank",
    "kotak": "Kotak Mahindra Bank",
    "dominos": "Domino's Pizza",
    "domino's": "Domino's Pizza",
    "google": "Alphabet Inc.",
    "alphabet": "Alphabet Inc.",
    "amazon": "Amazon",
    "apple": "Apple Inc.",
    "tesla": "Tesla Inc.",
    "meta": "Meta",
    "facebook": "Meta"
}

DISPLAY_TO_MARKET_ENTITY = {
    "Domino's Pizza": "Jubilant FoodWorks"
}


def normalize_entity(raw_name: str) -> dict:
    if not raw_name:
        return {
            "display_name": "Unknown",
            "market_entity": "Unknown"
        }

    cleaned = raw_name.strip().lower()

    if cleaned in ENTITY_MAP:
        display_name = ENTITY_MAP[cleaned]
    else:
        display_name = raw_name.strip()
        for key, value in ENTITY_MAP.items():
            if key in cleaned:
                display_name = value
                break

    market_entity = DISPLAY_TO_MARKET_ENTITY.get(display_name, display_name)

    return {
        "display_name": display_name,
        "market_entity": market_entity
    }