import requests
import json

# Test backend health
print("Testing backend health...")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"✓ Health check: {response.json()}")
except Exception as e:
    print(f"✗ Health check failed: {e}")

# Test headline analysis
print("\nTesting headline analysis...")
try:
    response = requests.post(
        "http://localhost:8000/api/v1/analysis/",
        json={"headline": "Tesla stock surges 10% on strong earnings report"}
    )
    print(f"✓ Analysis status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Risk Score: {data['risk_score']}")
        print(f"  Trading Signal: {data['trading_signal']}")
        print(f"  Entities: {len(data['entities']['companies'])} detected")
    else:
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"✗ Analysis failed: {e}")

# Test market data
print("\nTesting market data...")
try:
    response = requests.get("http://localhost:8000/api/v1/market/TSLA")
    print(f"✓ Market data status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"  Symbol: {data['data']['symbol']}")
            print(f"  Price: ${data['data']['price']:.2f}")
            print(f"  Change: {data['data']['changePercent']:.2f}%")
            print(f"  7-day Prediction: ${data['data']['prediction']['predicted_price']:.2f}")
    else:
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"✗ Market data failed: {e}")

# Test company search
print("\nTesting company search...")
try:
    response = requests.get("http://localhost:8000/api/v1/market/search?q=tesla")
    print(f"✓ Search status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Found {len(data['data'])} results")
        if data['data']:
            print(f"  First result: {data['data'][0]['name']}")
    else:
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"✗ Search failed: {e}")

# Test news endpoint
print("\nTesting news endpoint...")
try:
    response = requests.get("http://localhost:8000/api/v1/market/TSLA/news")
    print(f"✓ News status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Found {len(data['data'])} news articles")
        if data['data']:
            print(f"  Latest: {data['data'][0]['title'][:60]}...")
    else:
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"✗ News failed: {e}")

print("\n" + "="*50)
print("API Testing Complete!")
