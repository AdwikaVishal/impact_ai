"""
test_intelligence.py – Test the full intelligence pipeline with Groq.

Run from the backend/ directory:
    python test_intelligence.py
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.intelligence.enricher import enrich_company_data
from app.services.orchestrator import collect_raw_data


async def test_company(company_name: str, category: str) -> None:
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"📊  TESTING: {company_name.upper()}")
    print(sep)

    # Step 1 – raw scrape
    print(f"\n📡  Fetching raw data for {company_name}...")
    raw = await collect_raw_data(company_name, category)
    print(f"✅  Raw data received:")
    print(f"    Website:    {raw.get('website', 'N/A')}")
    print(f"    News:       {len(raw.get('brand_activity', []))} articles")
    print(f"    Competitors:{len(raw.get('competitors', []))}")
    print(f"    Contacts:   {len(raw.get('contacts_raw', []))}")
    print(f"    Events:     {len(raw.get('events', []))}")

    # Step 2 – Groq enrichment
    print(f"\n🧠  Generating intelligence with Groq (10-20 s)...")
    enriched = await enrich_company_data(raw)

    print(f"\n{'─'*50}")
    print(f"📋  INTELLIGENCE OUTPUTS – {company_name.upper()}")
    print(f"{'─'*50}")

    print(f"\n📌  #1 Company Overview:")
    print(f"    {enriched.get('company_overview', 'N/A')[:300]}")

    print(f"\n📌  #2 Market Position:")
    print(f"    {enriched.get('market_position', 'N/A')[:250]}")

    print(f"\n📌  #3 Competitor Mapping:")
    for c in enriched.get("competitor_mapping", [])[:3]:
        print(f"    • {c.get('name')}")
        print(f"      Strength: {c.get('strength', 'N/A')}")
        print(f"      Gap:      {c.get('gap', 'N/A')}")

    print(f"\n📌  #4 Brand Activity:")
    print(f"    {enriched.get('brand_activity', {}).get('summary', 'N/A')}")

    print(f"\n📌  #5 Events Footprint:")
    print(f"    {enriched.get('events_footprint', {}).get('summary', 'N/A')}")

    print(f"\n📌  #6 Strategic Watchouts:")
    for w in enriched.get("strategic_watchouts", []):
        print(f"    ⚠️  {w}")

    print(f"\n📌  #7/#8/#9 Decision Makers & Outreach:")
    for contact in enriched.get("decision_makers", [])[:2]:
        print(f"\n    👤 {contact.get('name')} ({contact.get('role')})")
        print(f"       Email:   {contact.get('email')}")
        print(f"       LinkedIn:{str(contact.get('linkedin_url', 'N/A'))[:60]}")
        print(f"\n       💬 LinkedIn Message:")
        print(f"          {contact.get('linkedin_message', 'N/A')[:200]}")
        print(f"\n       📧 Subject: {contact.get('email_subject', 'N/A')}")
        print(f"       📧 Body:    {contact.get('email_body', 'N/A')[:150]}...")

    # Save output
    os.makedirs("data", exist_ok=True)
    out_path = f"data/enriched_{company_name.lower()}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾  Saved → {out_path}")
    print(f"\n✅  {company_name} – ALL OUTPUTS GENERATED!")


async def main() -> None:
    print("\n" + "=" * 70)
    print("🧠  FULL INTELLIGENCE PIPELINE TEST (Groq)")
    print("=" * 70)

    test_cases = [
        ("Stripe",  "payment processing"),
        ("Nike",    "athletic footwear"),
        ("Spotify", "music streaming"),
    ]

    for company, category in test_cases:
        await test_company(company, category)

    print("\n" + "=" * 70)
    print("🎉  ALL TESTS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
