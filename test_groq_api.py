#!/usr/bin/env python3
"""
Test Groq API Integration
Fast LLM inference with Llama models
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.llm_client import get_groq_client

def test_groq_api():
    """Test Groq API with a sample headline"""
    print("\n" + "="*70)
    print("Testing Groq API Integration")
    print("="*70 + "\n")
    
    # Get client
    client = get_groq_client()
    
    if not client.api_key:
        print("❌ ERROR: GROQ_API_KEY not found in backend/.env")
        return False
    
    print(f"✓ API Key found: {client.api_key[:20]}...")
    print(f"✓ Model: {client.model}")
    print(f"✓ Endpoint: {client.base_url}\n")
    
    # Test headline
    test_headline = "Tesla stock surges 10% on strong earnings report"
    
    print(f"Testing with headline: '{test_headline}'")
    print("\nCalling Groq API...")
    
    try:
        result = client.analyze_headline(test_headline)
        
        if result and result.get('success'):
            print("\n✅ SUCCESS! Groq API is working\n")
            print("="*70)
            print("GROQ ANALYSIS:")
            print("="*70)
            print(result.get('analysis', 'No analysis returned'))
            print("="*70)
            print(f"\nModel used: {result.get('model')}")
            return True
        else:
            print("\n❌ FAILED: No response from Groq API")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_explanation_generation():
    """Test explanation generation"""
    print("\n" + "="*70)
    print("Testing Explanation Generation")
    print("="*70 + "\n")
    
    client = get_groq_client()
    
    # Sample analysis data
    sample_data = {
        'risk_score': 'LOW',
        'trading_signal': 'BUY',
        'analysis': {
            'sentiment': {'label': 'POSITIVE'},
            'fake_news_detection': {'fake_probability': 0.12}
        }
    }
    
    print("Generating explanation...")
    
    try:
        explanation = client.generate_explanation(sample_data)
        
        if explanation:
            print("\n✅ SUCCESS! Explanation generated\n")
            print("="*70)
            print("EXPLANATION:")
            print("="*70)
            print(explanation)
            print("="*70)
            return True
        else:
            print("\n❌ FAILED: No explanation generated")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def test_quick_response():
    """Test response speed"""
    print("\n" + "="*70)
    print("Testing Response Speed")
    print("="*70 + "\n")
    
    import time
    import requests
    import os
    from dotenv import load_dotenv
    
    load_dotenv('backend/.env')
    api_key = os.getenv("GROQ_API_KEY")
    
    print("Sending quick test request...")
    start = time.time()
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "user", "content": "Say 'Hello from Groq!' if you can hear me."}
                ],
                "max_tokens": 20
            },
            timeout=30
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            message = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            print(f"\n✅ SUCCESS!")
            print(f"Response time: {elapsed:.2f} seconds")
            print(f"Message: {message}")
            
            if elapsed < 1:
                print(f"⚡ VERY FAST! (< 1 second)")
            elif elapsed < 3:
                print(f"✓ FAST (< 3 seconds)")
            else:
                print(f"⚠ SLOW (> 3 seconds)")
            
            return True
        else:
            print(f"\n❌ FAILED: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("GROQ API TEST SUITE")
    print("="*70)
    
    # Test 1: Quick Response
    test1_passed = test_quick_response()
    
    # Test 2: Headline Analysis
    test2_passed = test_groq_api()
    
    # Test 3: Explanation Generation (only if test 2 passed)
    test3_passed = False
    if test2_passed:
        test3_passed = test_explanation_generation()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Quick Response:         {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Headline Analysis:      {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"Explanation Generation: {'✅ PASS' if test3_passed else '❌ FAIL'}")
    print("="*70)
    
    if test1_passed and test2_passed and test3_passed:
        print("\n✅ All tests passed! Groq API is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Integrate into analysis endpoint")
        print("2. Add LLM-powered explanations to frontend")
        print("3. Consider caching responses to reduce API calls")
        print("\n💡 Benefits:")
        print("• Fast inference (< 1 second)")
        print("• Free tier: 14,400 requests/day")
        print("• High-quality Llama 3.3 70B model")
    elif test1_passed:
        print("\n⚠️  Basic API works, but advanced features failed.")
        print("Check the error messages above for details.")
    else:
        print("\n❌ Groq API integration failed. Please check:")
        print("1. API key is correct in backend/.env")
        print("2. Network connectivity")
        print("3. Groq API status: https://status.groq.com/")
        print("4. API documentation: https://console.groq.com/docs")

if __name__ == "__main__":
    main()
