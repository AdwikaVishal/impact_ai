"""
Simple Competitor Scraper - Uses known competitor data
"""

import asyncio

# Known competitors for common companies
KNOWN_COMPETITORS = {
    "Stripe": [
        {"name": "PayPal", "website": "https://paypal.com", "recent_activity": ["Launched new BNPL features", "Expanded crypto services"]},
        {"name": "Square", "website": "https://square.com", "recent_activity": ["Acquired Afterpay", "Expanded banking services"]},
        {"name": "Adyen", "website": "https://adyen.com", "recent_activity": ["Expanded into US market", "New partnership with eBay"]},
        {"name": "Braintree", "website": "https://braintreepayments.com", "recent_activity": ["Enhanced fraud detection", "Global expansion"]},
        {"name": "Authorize.net", "website": "https://authorize.net", "recent_activity": ["API updates", "Mobile SDK release"]},
    ],
    "Nike": [
        {"name": "Adidas", "website": "https://adidas.com", "recent_activity": ["New Yeezy line", "Sustainable materials launch"]},
        {"name": "Under Armour", "website": "https://underarmour.com", "recent_activity": ["Connected fitness platform", "NBA partnership"]},
        {"name": "Puma", "website": "https://puma.com", "recent_activity": ["Rihanna collaboration", "Esports expansion"]},
        {"name": "New Balance", "website": "https://newbalance.com", "recent_activity": ["Made in USA campaign", "Basketball shoe launch"]},
        {"name": "Reebok", "website": "https://reebok.com", "recent_activity": ["CrossFit partnership", "Retro sneaker releases"]},
    ],
    "Spotify": [
        {"name": "Apple Music", "website": "https://apple.com/music", "recent_activity": ["Spatial audio expansion", "Exclusive artist deals"]},
        {"name": "Amazon Music", "website": "https://music.amazon.com", "recent_activity": ["HD streaming", "Podcast integration"]},
        {"name": "YouTube Music", "website": "https://music.youtube.com", "recent_activity": ["Smart downloads", "Lyrics integration"]},
        {"name": "Tidal", "website": "https://tidal.com", "recent_activity": ["HiFi Plus tier", "Artist-owned platform"]},
        {"name": "Deezer", "website": "https://deezer.com", "recent_activity": ["Flow AI playlist", "Car integration"]},
    ],
}

async def find_competitors_simple(company_name: str, category: str) -> list:
    """Return known competitors for the company."""
    
    # Try to find in known competitors
    if company_name in KNOWN_COMPETITORS:
        return KNOWN_COMPETITORS[company_name]
    
    # Fallback: generate based on category
    category_keywords = {
        "payment": ["PayPal", "Square", "Adyen", "Braintree"],
        "footwear": ["Adidas", "Under Armour", "Puma", "New Balance"],
        "music": ["Apple Music", "Amazon Music", "YouTube Music", "Tidal"],
        "streaming": ["Apple Music", "Amazon Music", "YouTube Music", "Tidal"],
    }
    
    # Find matching category
    for key, comps in category_keywords.items():
        if key in category.lower():
            return [{"name": c, "website": f"https://{c.lower().replace(' ', '')}.com", "recent_activity": []} for c in comps]
    
    return []


async def find_competitors(company_name: str, category: str) -> list:
    """Alias for find_competitors_simple"""
    return await find_competitors_simple(company_name, category)