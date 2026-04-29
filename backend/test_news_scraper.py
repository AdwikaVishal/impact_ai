"""
Test script for News Scraper
Run: python test_news_scraper.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.news_scraper import get_news_headlines

async def test_news_scraper():
    print("\n" + "="*60)
    print("🧪 TESTING NEWS SCRAPER")
    print("="*60)
    
    companies = ["Stripe", "Nike", "Spotify"]
    
    for company in companies:
        print(f"\n📊 Fetching news for: {company}")
        print("-" * 40)
        
        try:
            # Use days_back instead of months_back (365 days = 12 months)
            news = await get_news_headlines(company, days_back=365)
            
            if news:
                print(f"✅ Found {len(news)} articles")
                for i, article in enumerate(news[:5], 1):
                    print(f"\n   {i}. {article.get('title', 'N/A')[:80]}")
                    print(f"      Date: {article.get('date', 'N/A')}")
                    print(f"      Source: {article.get('source', 'N/A')}")
            else:
                print(f"⚠️ No news found for {company}")
                print("   Check your NEWSAPI_KEY in .env")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
    
    print("\n" + "="*60)
    print("✅ News scraper test complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_news_scraper())