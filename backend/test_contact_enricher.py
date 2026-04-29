"""
Test script for Contact Enricher
Run: python test_contact_enricher.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.contact_enricher import enrich_contacts, guess_email

async def test_contact_enricher():
    print("\n" + "="*60)
    print("🧪 TESTING CONTACT ENRICHER")
    print("="*60)
    
    # Test 1: Email guessing function
    print("\n📧 TEST 1: Email Guessing")
    print("-" * 40)
    
    test_cases = [
        ("John Doe", "stripe.com"),
        ("Jane Smith", "nike.com"),
        ("Michael Chen", "spotify.com"),
        ("Sarah Johnson", "google.com"),
    ]
    
    for name, domain in test_cases:
        result = guess_email(name, domain)
        print(f"   {name:20} @ {domain:15} → {result}")
    
    # Test 2: Full enrichment with real people data
    print("\n👥 TEST 2: Full Contact Enrichment")
    print("-" * 40)
    
    # People found from your people scraper
    test_people = [
        {"name": "Dan Davidow", "role": "CMO", "linkedin_url": "https://www.linkedin.com/in/dandavidow"},
        {"name": "Eric Bergevin", "role": "Chief Marketing Officer", "linkedin_url": "https://ca.linkedin.com/in/eric-bergevin-29b7a9b1"},
        {"name": "Adam Kerin", "role": "VP of Marketing", "linkedin_url": "https://www.linkedin.com/in/adamkerin"},
        {"name": "Sebastian Niemeyer", "role": "CMO", "linkedin_url": "https://de.linkedin.com/in/sebastian-niemeyer-2601"},
        {"name": "Neha Ahuja", "role": "CMO", "linkedin_url": "https://sg.linkedin.com/in/neha-ahuja-96029457"},
    ]
    
    domain = "stripe.com"
    
    enriched = await enrich_contacts(test_people, domain, "Test Company")
    
    print(f"\n   Enriched {len(enriched)} contacts:")
    for contact in enriched:
        print(f"\n   📌 {contact['name']} ({contact['role']})")
        print(f"      Email: {contact['email']}")
        print(f"      LinkedIn: {contact['linkedin_url'][:60]}...")
        print(f"      Confidence: {contact['confidence']}")
    
    print("\n" + "="*60)
    print("✅ Contact enricher test complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_contact_enricher())