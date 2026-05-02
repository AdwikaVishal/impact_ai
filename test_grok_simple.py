#!/usr/bin/env python3
"""
Simple Grok API Test - Try different configurations
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv("GROQ_API_KEY")

print("\n" + "="*70)
print("GROK API KEY TEST")
print("="*70)
print(f"\nAPI Key: {API_KEY[:20]}...{API_KEY[-10:]}")
print(f"Key Length: {len(API_KEY)}")
print(f"Key Prefix: {API_KEY[:4]}")

# Test configurations to try
configs = [
    {
        "name": "xAI Grok API (Official)",
        "url": "https://api.x.ai/v1/chat/completions",
        "model": "grok-beta"
    },
    {
        "name": "xAI Grok API (grok-2-1212)",
        "url": "https://api.x.ai/v1/chat/completions",
        "model": "grok-2-1212"
    },
    {
        "name": "xAI Grok API (grok-2)",
        "url": "https://api.x.ai/v1/chat/completions",
        "model": "grok-2"
    },
    {
        "name": "xAI Grok API (grok-1)",
        "url": "https://api.x.ai/v1/chat/completions",
        "model": "grok-1"
    },
    {
        "name": "Alternative endpoint (api.grok.x.ai)",
        "url": "https://api.grok.x.ai/v1/chat/completions",
        "model": "grok-beta"
    },
]

def test_config(config):
    """Test a specific API configuration"""
    print(f"\n{'='*70}")
    print(f"Testing: {config['name']}")
    print(f"URL: {config['url']}")
    print(f"Model: {config['model']}")
    print(f"{'='*70}")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": config['model'],
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Say 'Hello, I am Grok!' if you can hear me."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        print("\nSending request...")
        response = requests.post(
            config['url'],
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            data = response.json()
            print("\nResponse:")
            print(json.dumps(data, indent=2))
            
            # Extract message
            if 'choices' in data and len(data['choices']) > 0:
                message = data['choices'][0].get('message', {}).get('content', '')
                print(f"\n🤖 Grok says: {message}")
            
            return True
        else:
            print(f"❌ FAILED")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Request took too long")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR - {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR - {e}")
        return False

def test_models_endpoint():
    """Try to list available models"""
    print(f"\n{'='*70}")
    print("Testing: List Available Models")
    print(f"{'='*70}")
    
    endpoints = [
        "https://api.x.ai/v1/models",
        "https://api.grok.x.ai/v1/models",
    ]
    
    for endpoint in endpoints:
        print(f"\nTrying: {endpoint}")
        try:
            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {API_KEY}"},
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! Available models:")
                data = response.json()
                print(json.dumps(data, indent=2))
                return True
            else:
                print(f"Response: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")
    
    return False

def main():
    if not API_KEY:
        print("\n❌ ERROR: GROQ_API_KEY not found in backend/.env")
        return
    
    # First, try to list available models
    print("\n" + "="*70)
    print("STEP 1: Discover Available Models")
    print("="*70)
    models_found = test_models_endpoint()
    
    # Test each configuration
    print("\n" + "="*70)
    print("STEP 2: Test Different Configurations")
    print("="*70)
    
    success = False
    for config in configs:
        if test_config(config):
            success = True
            print(f"\n✅ WORKING CONFIGURATION FOUND!")
            print(f"   URL: {config['url']}")
            print(f"   Model: {config['model']}")
            break
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    if success:
        print("\n✅ Grok API is working!")
        print("\nNext steps:")
        print("1. Update llm_client.py with working configuration")
        print("2. Integrate into analysis endpoint")
        print("3. Test with real headlines")
    else:
        print("\n❌ All configurations failed")
        print("\nPossible reasons:")
        print("1. API key may be invalid or expired")
        print("2. xAI API may not be publicly available yet")
        print("3. Need to check xAI documentation: https://docs.x.ai/")
        print("4. May need to request API access from xAI")
        print("\nAlternatives:")
        print("- Use OpenAI GPT-4 API")
        print("- Use Anthropic Claude API")
        print("- Use Groq API (fast inference)")
        print("- Continue with rule-based system (works well)")

if __name__ == "__main__":
    main()
