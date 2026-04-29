"""
Test script for People Scraper (Decision Makers)
Run: python test_people_scraper.py
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the scraper
from app.scrapers.decision_maker_scraper import find_decision_makers

async def test_people_scraper():
    print("\n" + "="*60)
    print("🧪 TESTING PEOPLE SCRAPER (REAL DATA)")
    print("="*60)
    
    # Test companies
    test_companies = [
        ("Stripe", "stripe.com"),
        ("Nike", "nike.com"),
        ("Spotify", "spotify.com")
    ]
    
    for company_name, domain in test_companies:
        print(f"\n📊 Testing: {company_name}")
        print("-" * 40)
        
        try:
            # Call the scraper
            people = await find_decision_makers(company_name, domain, max_results=5)
            
            if people:
                print(f"✅ Found {len(people)} people")
                for i, person in enumerate(people, 1):
                    print(f"\n   {i}. Name: {person.get('name', 'Unknown')}")
                    print(f"      Role: {person.get('role', 'Unknown')}")
                    print(f"      Source: {person.get('source', 'Unknown')}")
                    print(f"      Confidence: {person.get('confidence', 'N/A')}")
                    if person.get('source_url'):
                        print(f"      LinkedIn: {person.get('source_url', 'N/A')[:80]}")
            else:
                print(f"⚠️ No people found for {company_name}")
                print("   This could be due to:")
                print("   - Rate limiting (wait 5 minutes)")
                print("   - No Serper key (check .env)")
                print("   - Company has no public LinkedIn profiles")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
    
    print("\n" + "="*60)
    print("✅ People scraper test complete")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_people_scraper())