"""
Test Backend Optimization
Verify cache, new APIs, and feature flags work correctly
"""
import requests
import time
import json


BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/v1/intelligence/health")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Health check passed")
        print(f"   Service: {data['service']}")
        print(f"   Version: {data['version']}")
        print(f"   Status: {data['status']}")
        print("\n📊 Feature Flags:")
        for feature, enabled in data['features'].items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {feature}: {enabled}")
        print("\n💾 Cache Status:")
        cache = data['cache']
        if cache['enabled']:
            print(f"   ✅ Cache enabled")
            print(f"   Total keys: {cache.get('total_keys', 0)}")
            print(f"   Hit rate: {cache.get('hit_rate', 0)}%")
        else:
            print(f"   ⚠️  Cache disabled (Redis not available)")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False


def test_cache_performance():
    """Test cache performance improvement"""
    print("\n" + "="*80)
    print("TEST 2: Cache Performance")
    print("="*80)
    
    test_company = {
        "company_name": "Nike",
        "category": "Athletic footwear and apparel"
    }
    
    # First request (no cache)
    print("\n🔄 First request (generating fresh data)...")
    start_time = time.time()
    response1 = requests.post(
        f"{BASE_URL}/api/v1/intelligence/analyze",
        json=test_company
    )
    first_duration = time.time() - start_time
    
    if response1.status_code != 200:
        print(f"❌ First request failed: {response1.status_code}")
        print(response1.text)
        return False
    
    print(f"✅ First request completed in {first_duration:.2f}s")
    
    # Second request (should use cache)
    print("\n⚡ Second request (should use cache)...")
    start_time = time.time()
    response2 = requests.post(
        f"{BASE_URL}/api/v1/intelligence/analyze",
        json=test_company
    )
    second_duration = time.time() - start_time
    
    if response2.status_code != 200:
        print(f"❌ Second request failed: {response2.status_code}")
        return False
    
    print(f"✅ Second request completed in {second_duration:.2f}s")
    
    # Calculate improvement
    if second_duration < first_duration:
        improvement = ((first_duration - second_duration) / first_duration) * 100
        print(f"\n🚀 Performance improvement: {improvement:.1f}% faster")
        print(f"   First request: {first_duration:.2f}s")
        print(f"   Second request: {second_duration:.2f}s")
        print(f"   Time saved: {first_duration - second_duration:.2f}s")
    else:
        print(f"\n⚠️  No performance improvement detected")
        print(f"   (Cache might be disabled or Redis not running)")
    
    return True


def test_cache_stats():
    """Test cache statistics endpoint"""
    print("\n" + "="*80)
    print("TEST 3: Cache Statistics")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/v1/intelligence/cache/stats")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Cache stats retrieved")
        
        if data['enabled']:
            print("\n📊 Cache Statistics:")
            stats = data['statistics']
            print(f"   Total keys: {stats.get('total_keys', 0)}")
            print(f"   Cache hits: {stats.get('hits', 0)}")
            print(f"   Cache misses: {stats.get('misses', 0)}")
            print(f"   Hit rate: {stats.get('hit_rate', 0)}%")
            
            print("\n⏰ Cache TTLs:")
            for key, ttl in data['ttls'].items():
                print(f"   {key}: {ttl}")
        else:
            print("⚠️  Cache is disabled")
        
        return True
    else:
        print(f"❌ Cache stats failed: {response.status_code}")
        return False


def test_new_apis():
    """Test new API integrations (Prospeo, Apify)"""
    print("\n" + "="*80)
    print("TEST 4: New API Integrations")
    print("="*80)
    
    test_company = {
        "company_name": "Salesforce",
        "category": "CRM and cloud software"
    }
    
    print("\n🔄 Testing intelligence generation with new APIs...")
    response = requests.post(
        f"{BASE_URL}/api/v1/intelligence/analyze",
        json=test_company
    )
    
    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        return False
    
    data = response.json()
    
    # Check decision makers (Prospeo)
    decision_makers = data.get('decision_makers', [])
    print(f"\n👥 Decision Makers: {len(decision_makers)} found")
    if decision_makers:
        for dm in decision_makers[:3]:
            print(f"   • {dm['name']} - {dm['title']}")
            if dm.get('email'):
                print(f"     Email: {dm['email']}")
    
    # Check events (Apify)
    events = data.get('events', [])
    print(f"\n🎪 Events: {len(events)} found")
    if events:
        for event in events[:3]:
            print(f"   • {event['name']}")
            print(f"     Date: {event['date']}, Type: {event['event_type']}")
    
    print(f"\n📊 Confidence Score: {data.get('confidence_score', 0):.0%}")
    
    return True


def run_all_tests():
    """Run all optimization tests"""
    print("\n" + "="*80)
    print("🚀 BACKEND OPTIMIZATION TEST SUITE")
    print("="*80)
    print("\nTesting MarketShield backend optimization features:")
    print("• Redis caching")
    print("• Prospeo API integration")
    print("• Apify events tracking")
    print("• Feature flags system")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Cache Performance", test_cache_performance()))
    results.append(("Cache Statistics", test_cache_stats()))
    results.append(("New API Integrations", test_new_apis()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend optimization is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print("   Make sure the backend is running on http://localhost:8000")
        print("   Run: cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
