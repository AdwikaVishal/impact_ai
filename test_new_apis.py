"""
Test script for new APIs: Prospeo and Apify
"""
import sys
sys.path.insert(0, 'backend')

from app.intelligence.decision_maker_finder_v2 import DecisionMakerFinder
from app.intelligence.events_tracker import EventsTracker

print("="*80)
print("🧪 TESTING NEW APIs - Prospeo & Apify")
print("="*80)
print()

# Test 1: Prospeo API (Decision Makers)
print("Test 1: Prospeo API - Decision Makers")
print("-"*80)
try:
    finder = DecisionMakerFinder()
    decision_makers = finder.find_decision_makers("Tesla", "tesla.com", "Automotive")

    if decision_makers:
        print(f"✅ Found {len(decision_makers)} decision makers")
        for i, dm in enumerate(decision_makers[:3], 1):
            print(f"\n   {i}. {dm.name}")
            print(f"      Title: {dm.title}")
            print(f"      Email: {dm.email or 'N/A'}")
            print(f"      Phone: {dm.phone or 'N/A'}")
            print(f"      LinkedIn: {dm.linkedin_url or 'N/A'}")
            print(f"      Relevance: {dm.relevance_score:.0%}")
    else:
        print("⚠️  No decision makers found (using fallback)")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 2: Apify API (Events)
print("Test 2: Apify API - Events")
print("-"*80)
try:
    tracker = EventsTracker()
    events = tracker.track_events("Tesla")

    if events:
        print(f"✅ Found {len(events)} events")
        for i, event in enumerate(events[:3], 1):
            print(f"\n   {i}. {event.name}")
            print(f"      Date: {event.date}")
            print(f"      Type: {event.event_type}")
            print(f"      Format: {event.format}")
            print(f"      Scale: {event.estimated_scale}")
    else:
        print("⚠️  No events found (using placeholder)")
except Exception as e:
    print(f"❌ Error: {e}")
print()

print("="*80)
print("✅ TESTING COMPLETE")
print("="*80)
print()
print("Next Steps:")
print("1. Update orchestrator to use new modules")
print("2. Test with multiple companies")
print("3. Monitor API usage and costs")
