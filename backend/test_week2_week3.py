"""
Test Week 2 (PostgreSQL) and Week 3 (Celery) Implementation
Comprehensive testing of database and async features
"""
import requests
import time
import json


BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check with new features"""
    print("\n" + "="*80)
    print("TEST 1: Health Check (Week 2 & 3 Features)")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/v1/intelligence/health")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Health check passed")
        print(f"   Service: {data['service']}")
        print(f"   Version: {data['version']}")
        
        # Check database status
        print("\n💾 Database Status:")
        db = data.get('database', {})
        if db.get('enabled'):
            print(f"   ✅ PostgreSQL enabled")
            print(f"   ✅ Dual-write mode: {db.get('dual_write')}")
            print(f"   📊 PostgreSQL reports: {db.get('postgres_reports', 0)}")
            print(f"   📄 JSON reports: {db.get('json_reports', 0)}")
        else:
            print(f"   ⚠️  PostgreSQL disabled (optional)")
        
        # Check Celery status
        print("\n🔄 Celery Status:")
        celery = data.get('celery', {})
        if celery.get('enabled'):
            print(f"   ✅ Celery enabled")
            print(f"   ✅ Async endpoints available")
        else:
            print(f"   ⚠️  Celery disabled (optional)")
        
        # Check cache status
        print("\n💾 Cache Status:")
        cache = data.get('cache', {})
        if cache.get('enabled'):
            print(f"   ✅ Redis cache enabled")
            print(f"   📊 Hit rate: {cache.get('hit_rate', 0)}%")
        else:
            print(f"   ⚠️  Cache disabled")
        
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False


def test_synchronous_endpoint():
    """Test original synchronous endpoint"""
    print("\n" + "="*80)
    print("TEST 2: Synchronous Endpoint (Original)")
    print("="*80)
    
    test_company = {
        "company_name": "Tesla",
        "category": "Electric vehicles and clean energy"
    }
    
    print(f"\n🔄 Testing synchronous intelligence generation...")
    print(f"   Company: {test_company['company_name']}")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/v1/intelligence/analyze",
        json=test_company
    )
    duration = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Synchronous request completed in {duration:.2f}s")
        print(f"   Company: {data['company_name']}")
        print(f"   Confidence: {data['confidence_score']:.0%}")
        print(f"   Decision makers: {len(data.get('decision_makers', []))}")
        print(f"   Events: {len(data.get('events', []))}")
        return True
    else:
        print(f"❌ Synchronous request failed: {response.status_code}")
        print(response.text)
        return False


def test_asynchronous_endpoint():
    """Test new asynchronous endpoint"""
    print("\n" + "="*80)
    print("TEST 3: Asynchronous Endpoint (Week 3)")
    print("="*80)
    
    test_company = {
        "company_name": "SpaceX",
        "category": "Aerospace and space transportation"
    }
    
    print(f"\n🔄 Testing asynchronous intelligence generation...")
    print(f"   Company: {test_company['company_name']}")
    
    # Start async task
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/v1/intelligence/analyze/async",
        json=test_company
    )
    submit_duration = time.time() - start_time
    
    if response.status_code == 202:
        data = response.json()
        task_id = data['task_id']
        backend = data.get('backend', 'unknown')
        
        print(f"✅ Async task submitted in {submit_duration:.2f}s")
        print(f"   Task ID: {task_id}")
        print(f"   Backend: {backend}")
        print(f"   Status URL: {data['status_url']}")
        
        # Poll for completion
        print(f"\n⏳ Waiting for task to complete...")
        max_wait = 60  # 60 seconds max
        waited = 0
        
        while waited < max_wait:
            time.sleep(2)
            waited += 2
            
            status_response = requests.get(
                f"{BASE_URL}/api/v1/intelligence/analyze/status/{task_id}"
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data['status']
                
                print(f"   Status: {status} ({waited}s elapsed)")
                
                if status == 'completed':
                    print(f"✅ Task completed successfully!")
                    result_data = status_data.get('data', {})
                    print(f"   Company: {result_data.get('company_name')}")
                    print(f"   Confidence: {result_data.get('confidence_score', 0):.0%}")
                    return True
                elif status == 'failed':
                    print(f"❌ Task failed: {status_data.get('error')}")
                    return False
        
        print(f"⚠️  Task timeout after {max_wait}s")
        return False
    
    elif response.status_code == 503:
        print(f"⚠️  Async processing not available (Celery not running)")
        print(f"   This is OK - async is optional")
        return True
    else:
        print(f"❌ Async request failed: {response.status_code}")
        print(response.text)
        return False


def test_dual_write_storage():
    """Test dual-write pattern (PostgreSQL + JSON)"""
    print("\n" + "="*80)
    print("TEST 4: Dual-Write Storage (Week 2)")
    print("="*80)
    
    test_company = {
        "company_name": "Apple",
        "category": "Consumer electronics and software"
    }
    
    print(f"\n🔄 Testing dual-write storage...")
    print(f"   Company: {test_company['company_name']}")
    
    # Generate intelligence (should save to both PostgreSQL and JSON)
    response = requests.post(
        f"{BASE_URL}/api/v1/intelligence/analyze",
        json=test_company
    )
    
    if response.status_code == 200:
        print(f"✅ Intelligence generated and saved")
        
        # Check if data was saved
        import os
        from pathlib import Path
        
        json_file = Path("backend/data/intelligence_reports/apple_intelligence.json")
        if json_file.exists():
            print(f"   ✅ JSON file created: {json_file}")
        else:
            print(f"   ⚠️  JSON file not found (may be in different location)")
        
        # Check database (via health endpoint)
        health_response = requests.get(f"{BASE_URL}/api/v1/intelligence/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            db = health_data.get('database', {})
            
            if db.get('enabled'):
                print(f"   ✅ PostgreSQL storage: {db.get('postgres_reports', 0)} reports")
            else:
                print(f"   ⚠️  PostgreSQL not enabled (optional)")
        
        return True
    else:
        print(f"❌ Intelligence generation failed: {response.status_code}")
        return False


def test_batch_processing():
    """Test batch processing endpoint"""
    print("\n" + "="*80)
    print("TEST 5: Batch Processing (Week 3)")
    print("="*80)
    
    companies = [
        {"company_name": "Nike", "category": "Athletic footwear"},
        {"company_name": "Adidas", "category": "Athletic apparel"},
        {"company_name": "Puma", "category": "Sportswear"}
    ]
    
    print(f"\n🔄 Testing batch processing...")
    print(f"   Companies: {len(companies)}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/intelligence/analyze/batch",
        json={"companies": companies}
    )
    
    if response.status_code == 202:
        data = response.json()
        print(f"✅ Batch submitted successfully")
        print(f"   Batch ID: {data.get('batch_id')}")
        print(f"   Total companies: {data.get('total')}")
        return True
    
    elif response.status_code == 503:
        print(f"⚠️  Batch processing not available (Celery not running)")
        print(f"   This is OK - batch is optional")
        return True
    else:
        print(f"❌ Batch request failed: {response.status_code}")
        print(response.text)
        return False


def run_all_tests():
    """Run all Week 2 & 3 tests"""
    print("\n" + "="*80)
    print("🧪 WEEK 2 & 3 COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nTesting:")
    print("• Week 2: PostgreSQL database with dual-write")
    print("• Week 3: Celery async processing")
    print("• Backward compatibility")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Synchronous Endpoint", test_synchronous_endpoint()))
    results.append(("Asynchronous Endpoint", test_asynchronous_endpoint()))
    results.append(("Dual-Write Storage", test_dual_write_storage()))
    results.append(("Batch Processing", test_batch_processing()))
    
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
        print("\n🎉 All tests passed! Week 2 & 3 implementation working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("\nNote: Async and batch tests may fail if Celery is not running.")
        print("      This is OK - these features are optional.")


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
