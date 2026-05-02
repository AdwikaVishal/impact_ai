"""
Test script for Market Intelligence Engine
"""
import requests
import json
from datetime import datetime


def test_intelligence_engine():
    """Test the intelligence engine with sample companies"""
    
    base_url = "http://localhost:8000"
    
    # Test companies across different industries
    test_companies = [
        {
            "company_name": "Tesla",
            "category": "Electric Vehicles & Clean Energy"
        },
        {
            "company_name": "Airbnb",
            "category": "Travel & Hospitality Technology"
        },
        {
            "company_name": "Stripe",
            "category": "Financial Technology & Payments"
        }
    ]
    
    print("="*80)
    print("🧪 MARKET INTELLIGENCE ENGINE - TEST SUITE")
    print("="*80)
    print()
    
    # Test 1: Health Check
    print("📋 Test 1: Health Check")
    print("-" * 80)
    try:
        response = requests.get(f"{base_url}/api/v1/intelligence/health", timeout=5)
        if response.status_code == 200:
            print("✅ Intelligence API is healthy")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    print()
    
    # Test 2: Generate Intelligence Reports
    print("📋 Test 2: Generate Intelligence Reports")
    print("-" * 80)
    
    for i, company in enumerate(test_companies, 1):
        print(f"\n🏢 Company {i}: {company['company_name']}")
        print(f"   Category: {company['category']}")
        print()
        
        try:
            # Make request
            response = requests.post(
                f"{base_url}/api/v1/intelligence/analyze",
                json=company,
                params={"opportunity_angle": "experiential marketing partnership"},
                timeout=60  # Intelligence gathering takes time
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Intelligence report generated successfully!")
                print()
                
                # Display key sections
                print("📊 COMPANY OVERVIEW:")
                print(f"   Business Model: {data['business_model'][:100]}...")
                print(f"   Positioning: {data['positioning'][:100]}...")
                print(f"   Scale: {data['scale_metrics']}")
                print()
                
                print("🎯 MARKET POSITION:")
                print(f"   Brand Perception: {data['brand_perception'][:150]}...")
                print(f"   Recent Shifts: {len(data['recent_shifts'])} detected")
                for shift in data['recent_shifts'][:2]:
                    print(f"      - {shift}")
                print()
                
                print("🏆 COMPETITORS:")
                print(f"   Found: {len(data['competitors'])} competitors")
                for comp in data['competitors'][:3]:
                    print(f"      - {comp['name']} ({comp['domain']}) - Score: {comp['relevance_score']}")
                print()
                
                print("📅 BRAND ACTIVITIES:")
                print(f"   Tracked: {len(data['activities'])} activities")
                for activity in data['activities'][:3]:
                    print(f"      - [{activity['activity_type']}] {activity['title'][:60]}...")
                print()
                
                print("⚠️  STRATEGIC WATCHOUTS:")
                print(f"   Identified: {len(data['watchouts'])} watchouts")
                for watchout in data['watchouts']:
                    print(f"      - [{watchout['severity'].upper()}] {watchout['description']}")
                print()
                
                print("👥 DECISION MAKERS:")
                print(f"   Found: {len(data['decision_makers'])} decision makers")
                for dm in data['decision_makers'][:3]:
                    print(f"      - {dm['name']} - {dm['title']}")
                    if dm['email']:
                        print(f"        Email: {dm['email']}")
                    if dm['linkedin_url']:
                        print(f"        LinkedIn: {dm['linkedin_url']}")
                    print(f"        Relevance: {dm['relevance_score']:.0%}")
                print()
                
                print("✉️  PERSONALIZED OUTREACH:")
                if data['outreach_messages']:
                    if 'linkedin' in data['outreach_messages']:
                        linkedin = data['outreach_messages']['linkedin']
                        print(f"   LinkedIn Message:")
                        print(f"      {linkedin['message'][:200]}...")
                        print()
                    
                    if 'email' in data['outreach_messages']:
                        email = data['outreach_messages']['email']
                        print(f"   Email:")
                        print(f"      Subject: {email['subject']}")
                        print(f"      Body: {email['message'][:200]}...")
                        print()
                
                print("📈 METADATA:")
                print(f"   Confidence Score: {data['confidence_score']:.0%}")
                print(f"   Generated At: {data['generated_at']}")
                print()
                
                print("="*80)
                
            else:
                print(f"❌ Failed to generate intelligence: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️  Request timeout (intelligence gathering takes time)")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("="*80)
    print("✅ TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_intelligence_engine()
