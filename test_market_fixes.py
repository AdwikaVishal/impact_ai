#!/usr/bin/env python3
"""
Test script to verify market data and news API fixes
Tests both yfinance and Alpha Vantage backup
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_market_data():
    """Test market data endpoint with multiple symbols"""
    print_section("TESTING MARKET DATA ENDPOINT")
    
    test_symbols = [
        "NASDAQ:AAPL",
        "NASDAQ:TSLA", 
        "NSE:RELIANCE",
        "NASDAQ:MSFT"
    ]
    
    results = []
    
    for symbol in test_symbols:
        print(f"\n📊 Testing: {symbol}")
        try:
            response = requests.get(f"{BASE_URL}/api/v1/market/{symbol}", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    market_data = data.get("data", {})
                    source = market_data.get("source", "unknown")
                    
                    print(f"   ✅ SUCCESS (Source: {source})")
                    print(f"   📈 Price: ${market_data.get('price', 0):.2f}")
                    print(f"   📊 Change: {market_data.get('changePercent', 0):.2f}%")
                    print(f"   🔮 Prediction: ${market_data.get('prediction', {}).get('predicted_price', 0):.2f}")
                    
                    results.append({
                        "symbol": symbol,
                        "status": "✅ PASS",
                        "source": source,
                        "price": market_data.get('price', 0)
                    })
                else:
                    print(f"   ❌ FAIL: API returned success=false")
                    results.append({"symbol": symbol, "status": "❌ FAIL", "source": "none"})
            else:
                print(f"   ❌ FAIL: HTTP {response.status_code}")
                results.append({"symbol": symbol, "status": "❌ FAIL", "source": "none"})
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  TIMEOUT (15s)")
            results.append({"symbol": symbol, "status": "⏱️ TIMEOUT", "source": "none"})
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append({"symbol": symbol, "status": "❌ ERROR", "source": "none"})
    
    # Summary
    print("\n" + "-"*80)
    print("MARKET DATA SUMMARY:")
    print("-"*80)
    for result in results:
        print(f"  {result['symbol']:20} {result['status']:15} Source: {result.get('source', 'N/A')}")
    
    success_count = sum(1 for r in results if "✅" in r['status'])
    print(f"\n  Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.0f}%)")
    
    return results

def test_news_api():
    """Test news endpoint with NewsAPI integration"""
    print_section("TESTING NEWS ENDPOINT")
    
    test_symbols = [
        "NASDAQ:AAPL",
        "NASDAQ:TSLA",
        "NSE:RELIANCE"
    ]
    
    results = []
    
    for symbol in test_symbols:
        print(f"\n📰 Testing news for: {symbol}")
        try:
            response = requests.get(f"{BASE_URL}/api/v1/market/{symbol}/news", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    news_items = data.get("data", [])
                    source = data.get("source", "unknown")
                    
                    print(f"   ✅ SUCCESS (Source: {source})")
                    print(f"   📰 Articles: {len(news_items)}")
                    
                    if news_items:
                        print(f"   📌 Latest: {news_items[0].get('title', 'N/A')[:60]}...")
                    
                    results.append({
                        "symbol": symbol,
                        "status": "✅ PASS",
                        "source": source,
                        "count": len(news_items)
                    })
                else:
                    print(f"   ❌ FAIL: API returned success=false")
                    results.append({"symbol": symbol, "status": "❌ FAIL", "source": "none", "count": 0})
            else:
                print(f"   ❌ FAIL: HTTP {response.status_code}")
                results.append({"symbol": symbol, "status": "❌ FAIL", "source": "none", "count": 0})
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  TIMEOUT (15s)")
            results.append({"symbol": symbol, "status": "⏱️ TIMEOUT", "source": "none", "count": 0})
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append({"symbol": symbol, "status": "❌ ERROR", "source": "none", "count": 0})
    
    # Summary
    print("\n" + "-"*80)
    print("NEWS API SUMMARY:")
    print("-"*80)
    for result in results:
        print(f"  {result['symbol']:20} {result['status']:15} Source: {result.get('source', 'N/A'):10} Articles: {result.get('count', 0)}")
    
    success_count = sum(1 for r in results if "✅" in r['status'])
    print(f"\n  Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.0f}%)")
    
    return results

def test_health():
    """Test backend health"""
    print_section("TESTING BACKEND HEALTH")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend is not responding: {e}")
        return False

def main():
    print("\n" + "🔧"*40)
    print("  MARKETSHIELD API FIX VERIFICATION TEST")
    print("  Testing Alpha Vantage backup & NewsAPI integration")
    print("🔧"*40)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test health first
    if not test_health():
        print("\n❌ Backend is not running. Please start it first:")
        print("   cd backend && python -m uvicorn app.main:app --reload")
        return
    
    # Test market data
    market_results = test_market_data()
    
    # Test news
    news_results = test_news_api()
    
    # Final summary
    print("\n" + "="*80)
    print("  FINAL SUMMARY")
    print("="*80)
    
    market_success = sum(1 for r in market_results if "✅" in r['status'])
    news_success = sum(1 for r in news_results if "✅" in r['status'])
    
    print(f"\n📊 Market Data: {market_success}/{len(market_results)} working")
    print(f"📰 News API: {news_success}/{len(news_results)} working")
    
    # Check data sources
    av_count = sum(1 for r in market_results if r.get('source') == 'alpha_vantage')
    yf_count = sum(1 for r in market_results if r.get('source') == 'yfinance')
    newsapi_count = sum(1 for r in news_results if r.get('source') == 'newsapi')
    
    print(f"\n🔄 Data Sources:")
    print(f"   Alpha Vantage: {av_count} requests")
    print(f"   yfinance: {yf_count} requests")
    print(f"   NewsAPI: {newsapi_count} requests")
    
    total_success = market_success + news_success
    total_tests = len(market_results) + len(news_results)
    overall_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n🎯 Overall Success Rate: {overall_rate:.0f}%")
    
    if overall_rate >= 80:
        print("\n✅ EXCELLENT! Core issues are fixed!")
    elif overall_rate >= 60:
        print("\n⚠️  GOOD! Most issues are fixed, some improvements needed.")
    else:
        print("\n❌ NEEDS WORK! Core issues still present.")
    
    print("\n" + "="*80)
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
