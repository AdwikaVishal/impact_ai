"""
Run all tests for Person A
"""

import subprocess
import sys

tests = [
    ("test_people_scraper.py", "People Scraper"),
    ("test_contact_enricher.py", "Contact Enricher"),
    ("test_news_scraper.py", "News Scraper"),
    ("test_competitor_scraper.py", "Competitor Scraper"),
]

print("\n" + "="*60)
print("🚀 RUNNING ALL TESTS")
print("="*60)

for test_file, test_name in tests:
    print(f"\n📋 Testing: {test_name}")
    print("-"*40)
    result = subprocess.run([sys.executable, test_file], capture_output=False)
    
print("\n" + "="*60)
print("✅ All tests complete")