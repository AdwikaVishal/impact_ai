"""
Test script for Competitor Scraper
Run: python test_competitor_scraper.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.competitor_scraper import find_competitors

async def test_competitor_scraper():
    print("\n" + "="*60)
    print("🧪 TESTING COMPETITOR SCRAPER")
    print("="*60)
    
    test_companies = [
        ("Stripe", "payment processing"),
        ("Nike", "athletic footwear"),
        ("Spotify", "music streaming")
    ]
    
    for company_name, category in test_companies:
        print(f"\n📊 Finding competitors for: {company_name}")
        print("-" * 40)
        
        try:
            competitors = await find_competitors(company_name, category)
            
            if competitors:
                print(f"✅ Found {len(competitors)} competitors")
                for i, comp in enumerate(competitors[:5], 1):
                    print(f"\n   {i}. {comp.get('name', 'N/A')}")
                    print(f"      Website: {comp.get('website', 'N/A')}")
                    if comp.get('recent_activity'):
                        activity = comp['recent_activity'][0][:60] if comp['recent_activity'] else "None"
                        print(f"      Recent: {activity}")
            else:
                print(f"⚠️ No competitors found for {company_name}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
    
    print("\n" + "="*60)
    print("✅ Competitor scraper test complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_competitor_scraper())