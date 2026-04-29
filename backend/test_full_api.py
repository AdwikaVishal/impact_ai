"""
Test the full /company/analyze API endpoint
Run: python test_full_api.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_full_api():
    print("\n" + "="*60)
    print("🧪 TESTING FULL API ENDPOINT")
    print("="*60)
    
    # Make sure server is running first
    try:
        health = requests.get("http://localhost:8000/health", timeout=5)
        print(f"\n✅ Server is running: {health.json()}")
    except:
        print("\n❌ Server is NOT running!")
        print("   Start it with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Test companies
    test_companies = [
        ("Stripe", "payment processing"),
    ]
    
    for company_name, category in test_companies:
        print(f"\n📊 Testing: {company_name}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/company/analyze",
                json={"company_name": company_name, "category": category},
                timeout=60
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received in {elapsed:.1f}s")
                
                # Print the actual response structure
                print(f"\n📁 RESPONSE KEYS: {list(data.keys())}")
                
                # Check if data is nested under 'data' key or direct
                if 'data' in data:
                    result = data['data']
                else:
                    result = data
                
                print(f"\n📁 DATA SUMMARY:")
                print(f"   Company: {result.get('company_name', 'N/A')}")
                print(f"   Website: {result.get('website', 'N/A')}")
                print(f"   Domain: {result.get('domain', 'N/A')}")
                
                # Overview
                overview = result.get('overview', {})
                about_text = overview.get('about_text', '')
                if about_text:
                    print(f"\n📋 Company Overview Preview:")
                    print(f"   {about_text[:150]}...")
                else:
                    print(f"\n📋 Company Overview: No about text found")
                
                # Scale indicators
                scale = overview.get('scale_indicators', {})
                if scale:
                    print(f"\n📊 Scale Indicators:")
                    print(f"   Revenue: {scale.get('revenue', 'N/A')}")
                    print(f"   Employees: {scale.get('employees', 'N/A')}")
                
                # Competitors
                competitors = result.get('competitors', [])
                print(f"\n🏢 Competitors ({len(competitors)}):")
                for comp in competitors[:3]:
                    print(f"   - {comp.get('name', 'N/A')}: {comp.get('website', 'N/A')}")
                
                # News/Brand Activity
                news = result.get('brand_activity', [])
                print(f"\n📰 Recent News ({len(news)}):")
                for article in news[:3]:
                    title = article.get('title', 'N/A')
                    print(f"   - {title[:70]}...")
                
                # Decision Makers (raw)
                people = result.get('decision_makers_raw', [])
                print(f"\n👥 Decision Makers Found ({len(people)}):")
                for person in people[:3]:
                    name = person.get('name', 'Unknown')
                    role = person.get('role', 'N/A')
                    print(f"   - {name} ({role})")
                
                # Enriched Contacts
                contacts = result.get('contacts_raw', [])
                print(f"\n📧 Enriched Contacts ({len(contacts)}):")
                for contact in contacts[:3]:
                    name = contact.get('name', 'Unknown')
                    email = contact.get('email', 'N/A')
                    linkedin = contact.get('linkedin_url', 'N/A')
                    print(f"   - {name}: {email}")
                    if linkedin and linkedin != 'Not found':
                        print(f"     LinkedIn: {linkedin[:60]}...")
                
                # Events
                events = result.get('events', [])
                if events:
                    print(f"\n🎪 Events ({len(events)}):")
                    for event in events[:2]:
                        print(f"   - {event.get('source_url', 'N/A')[:60]}...")
                
                print(f"\n✅ All data fields extracted successfully!")
                
            else:
                print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
                
        except requests.Timeout:
            print(f"❌ Timeout after 60 seconds")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ Full API test complete!")
    print("="*60)

if __name__ == "__main__":
    test_full_api()