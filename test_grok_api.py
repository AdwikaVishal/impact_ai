#!/usr/bin/env python3
"""
Test xAI Grok API Integration
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.llm_client import get_grok_client

def test_grok_api():
    """Test Grok API with a sample headline"""
    print("\n" + "="*70)
    print("Testing xAI Grok API Integration")
    print("="*70 + "\n")
    
    # Get client
    client = get_grok_client()
    
    if not client.api_key:
        print("❌ ERROR: GROQ_API_KEY not found in backend/.env")
        print("\nPlease ensure backend/.env contains:")
        print("GROQ_API_KEY=your_groq_api_key_here")
        return False
    
    print(f"✓ API Key found: {client.api_key[:20]}...")
    print(f"✓ Model: {client.model}")
    print(f"✓ Endpoint: {client.base_url}\n")
    
    # Test headline
    test_headline = "Tesla stock surges 10% on strong earnings report"
    
    print(f"Testing with headline: '{test_headline}'")
    print("\nCalling Grok API...")
    
    try:
        result = client.analyze_headline(test_headline)
        
        if result and result.get('success'):
            print("\n✅ SUCCESS! Grok API is working\n")
            print("="*70)
            print("GROK ANALYSIS:")
            print("="*70)
            print(result.get('analysis', 'No analysis returned'))
            print("="*70)
            return True
        else:
            print("\n❌ FAILED: No response from Grok API")
            print("\nPossible issues:")
            print("1. API key may be invalid")
            print("2. xAI API endpoint may have changed")
            print("3. Network connectivity issues")
            print("4. API rate limit reached")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def test_explanation_generation():
    """Test explanation generation"""
    print("\n" + "="*70)
    print("Testing Explanation Generation")
    print("="*70 + "\n")
    
    client = get_grok_client()
    
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

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("xAI GROK API TEST SUITE")
    print("="*70)
    
    # Test 1: Headline Analysis
    test1_passed = test_grok_api()
    
    # Test 2: Explanation Generation (only if test 1 passed)
    test2_passed = False
    if test1_passed:
        test2_passed = test_explanation_generation()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Headline Analysis:      {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Explanation Generation: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print("="*70)
    
    if test1_passed and test2_passed:
        print("\n✅ All tests passed! Grok API is ready to use.")
        print("\nNext steps:")
        print("1. Integrate into analysis endpoint")
        print("2. Add LLM-powered explanations to frontend")
        print("3. Consider caching responses to reduce API calls")
    elif test1_passed:
        print("\n⚠️  Headline analysis works, but explanation generation failed.")
    else:
        print("\n❌ Grok API integration failed. Please check:")
        print("1. API key is correct")
        print("2. xAI API endpoint is correct")
        print("3. Network connectivity")
        print("4. API documentation: https://docs.x.ai/")

if __name__ == "__main__":
    main()
