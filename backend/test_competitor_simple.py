"""
Test simple competitor scraper
Run: python test_competitor_simple.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.competitor_scraper_simple import find_competitors_simple

async def test():
    print("\n" + "="*60)
    print("🧪 TESTING SIMPLE COMPETITOR SCRAPER")
    print("="*60)
    
    companies = [
        ("Stripe", "payment processing"),
        ("Nike", "athletic footwear"),
        ("Spotify", "music streaming")
    ]
    
    for company, category in companies:
        print(f"\n📊 Finding competitors for: {company}")
        print("-" * 40)
        
        competitors = await find_competitors_simple(company, category)
        
        if competitors:
            print(f"✅ Found {len(competitors)} competitors")
            for i, comp in enumerate(competitors, 1):
                print(f"   {i}. {comp['name']} - {comp['website']}")
        else:
            print(f"⚠️ No competitors found")

if __name__ == "__main__":
    asyncio.run(test())