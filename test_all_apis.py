#!/usr/bin/env python3
"""
Comprehensive API Test Suite
Tests all MarketShield APIs and external integrations
"""

import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('backend/.env')

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{text.center(70)}")
    print(f"{'='*70}{Colors.END}\n")

def print_test(name):
    print(f"{Colors.YELLOW}Testing: {name}...{Colors.END}", end=" ")

def print_success(message=""):
    print(f"{Colors.GREEN}✓ PASS{Colors.END}", end="")
    if message:
        print(f" - {message}")
    else:
        print()

def print_failure(message=""):
    print(f"{Colors.RED}✗ FAIL{Colors.END}", end="")
    if message:
        print(f" - {message}")
    else:
        print()

def print_warning(message=""):
    print(f"{Colors.YELLOW}⚠ WARN{Colors.END}", end="")
    if message:
        print(f" - {message}")
    else:
        print()

def print_info(key, value):
    print(f"  {Colors.BLUE}{key}:{Colors.END} {value}")

# Test Results Tracker
results = {
    'passed': 0,
    'failed': 0,
    'warnings': 0,
    'tests': []
}

def record_result(name, status, details=""):
    results['tests'].append({
        'name': name,
        'status': status,
        'details': details
    })
    if status == 'pass':
        results['passed'] += 1
    elif status == 'fail':
        results['failed'] += 1
    elif status == 'warn':
        results['warnings'] += 1

# ============================================================================
# BACKEND API TESTS
# ============================================================================

def test_backend_health():
    """Test backend server health"""
    print_header("BACKEND SERVER HEALTH CHECK")
    
    print_test("Backend Server Connection")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success()
            print_info("Status", data.get('status'))
            print_info("Service", data.get('service'))
            record_result("Backend Health", "pass")
            return True
        else:
            print_failure(f"Status {response.status_code}")
            record_result("Backend Health", "fail", f"Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_failure("Cannot connect - Server not running")
        record_result("Backend Health", "fail", "Server not running")
        return False
    except Exception as e:
        print_failure(str(e))
        record_result("Backend Health", "fail", str(e))
        return False

def test_headline_analysis():
    """Test headline analysis endpoint"""
    print_header("HEADLINE ANALYSIS API")
    
    test_headlines = [
        "Tesla stock surges 10% on strong earnings report",
        "Apple announces new iPhone with revolutionary features",
        "Bitcoin crashes 20% amid regulatory concerns"
    ]
    
    for i, headline in enumerate(test_headlines, 1):
        print_test(f"Analysis #{i}: '{headline[:40]}...'")
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/analysis/",
                json={"headline": headline},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success()
                print_info("Risk Score", data.get('risk_score'))
                print_info("Trading Signal", data.get('trading_signal'))
                print_info("Sentiment", data.get('analysis', {}).get('sentiment', {}).get('label'))
                record_result(f"Analysis #{i}", "pass")
            else:
                print_failure(f"Status {response.status_code}")
                record_result(f"Analysis #{i}", "fail", f"Status {response.status_code}")
        except Exception as e:
            print_failure(str(e))
            record_result(f"Analysis #{i}", "fail", str(e))

def test_company_search():
    """Test company search endpoint"""
    print_header("COMPANY SEARCH API")
    
    test_queries = ["tesla", "apple", "bitcoin"]
    
    for query in test_queries:
        print_test(f"Search: '{query}'")
        try:
            response = requests.get(
                f"http://localhost:8000/api/v1/market/search?q={query}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    results_data = data.get('data', [])
                    print_success()
                    print_info("Results", len(results_data))
                    if results_data:
                        print_info("First", f"{results_data[0].get('name')} ({results_data[0].get('symbol')})")
                    record_result(f"Search '{query}'", "pass")
                else:
                    print_failure("Success flag false")
                    record_result(f"Search '{query}'", "fail", "Success flag false")
            else:
                print_failure(f"Status {response.status_code}")
                record_result(f"Search '{query}'", "fail", f"Status {response.status_code}")
        except Exception as e:
            print_failure(str(e))
            record_result(f"Search '{query}'", "fail", str(e))

def test_market_data():
    """Test market data endpoint"""
    print_header("MARKET DATA API")
    
    test_symbols = [
        ("AAPL", "Apple"),
        ("TSLA", "Tesla"),
        ("MSFT", "Microsoft")
    ]
    
    for symbol, name in test_symbols:
        print_test(f"Market Data: {name} ({symbol})")
        try:
            response = requests.get(
                f"http://localhost:8000/api/v1/market/{symbol}",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    market_data = data.get('data', {})
                    print_success()
                    print_info("Price", f"${market_data.get('price', 0):.2f}")
                    print_info("Change", f"{market_data.get('changePercent', 0):.2f}%")
                    
                    prediction = market_data.get('prediction', {})
                    if prediction:
                        print_info("7-Day Prediction", f"${prediction.get('predicted_price', 0):.2f}")
                    record_result(f"Market Data {symbol}", "pass")
                else:
                    print_failure("Success flag false")
                    record_result(f"Market Data {symbol}", "fail", "Success flag false")
            elif response.status_code == 404:
                print_warning("No data (yfinance issue)")
                record_result(f"Market Data {symbol}", "warn", "yfinance rate limit")
            else:
                print_failure(f"Status {response.status_code}")
                record_result(f"Market Data {symbol}", "fail", f"Status {response.status_code}")
        except Exception as e:
            print_warning(str(e))
            record_result(f"Market Data {symbol}", "warn", str(e))

def test_news_endpoint():
    """Test news endpoint"""
    print_header("NEWS API")
    
    test_symbols = [("AAPL", "Apple"), ("TSLA", "Tesla")]
    
    for symbol, name in test_symbols:
        print_test(f"News: {name} ({symbol})")
        try:
            response = requests.get(
                f"http://localhost:8000/api/v1/market/{symbol}/news",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    news = data.get('data', [])
                    if len(news) > 0:
                        print_success()
                        print_info("Articles", len(news))
                        print_info("Latest", news[0].get('title', '')[:50] + "...")
                        record_result(f"News {symbol}", "pass")
                    else:
                        print_warning("No articles (yfinance)")
                        record_result(f"News {symbol}", "warn", "No articles")
                else:
                    print_failure("Success flag false")
                    record_result(f"News {symbol}", "fail", "Success flag false")
            else:
                print_failure(f"Status {response.status_code}")
                record_result(f"News {symbol}", "fail", f"Status {response.status_code}")
        except Exception as e:
            print_failure(str(e))
            record_result(f"News {symbol}", "fail", str(e))

# ============================================================================
# EXTERNAL API TESTS
# ============================================================================

def test_grok_api():
    """Test xAI Grok API"""
    print_header("xAI GROK API")
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print_test("Grok API Key")
        print_warning("Not configured")
        record_result("Grok API", "warn", "No API key")
        return
    
    print_test("Grok API Key")
    print_success(f"{api_key[:20]}...{api_key[-10:]}")
    
    print_test("Grok API Connection")
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "grok-beta",
                "messages": [
                    {"role": "user", "content": "Say 'Hello' if you can hear me."}
                ],
                "max_tokens": 10
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print_success("API Working!")
            data = response.json()
            message = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            print_info("Response", message)
            record_result("Grok API", "pass")
        elif response.status_code == 403:
            print_warning("No credits - Purchase at https://console.x.ai")
            record_result("Grok API", "warn", "No credits")
        elif response.status_code == 400:
            error = response.json().get('error', '')
            print_warning(f"Model issue: {error}")
            record_result("Grok API", "warn", error)
        else:
            print_failure(f"Status {response.status_code}")
            record_result("Grok API", "fail", f"Status {response.status_code}")
    except Exception as e:
        print_failure(str(e))
        record_result("Grok API", "fail", str(e))

def test_newsapi():
    """Test NewsAPI"""
    print_header("NEWSAPI")
    
    api_key = os.getenv("NEWSAPI_KEY")
    
    if not api_key:
        print_test("NewsAPI Key")
        print_warning("Not configured")
        record_result("NewsAPI", "warn", "No API key")
        return
    
    print_test("NewsAPI Key")
    print_success(f"{api_key[:20]}...")
    
    print_test("NewsAPI Connection")
    try:
        response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": "tesla",
                "apiKey": api_key,
                "pageSize": 5
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print_success()
            print_info("Articles Found", len(articles))
            if articles:
                print_info("Latest", articles[0].get('title', '')[:50] + "...")
            record_result("NewsAPI", "pass")
        else:
            print_failure(f"Status {response.status_code}")
            record_result("NewsAPI", "fail", f"Status {response.status_code}")
    except Exception as e:
        print_failure(str(e))
        record_result("NewsAPI", "fail", str(e))

def test_alpha_vantage():
    """Test Alpha Vantage API"""
    print_header("ALPHA VANTAGE API")
    
    api_key = os.getenv("ALPHA_VANTAGE_KEY")
    
    if not api_key:
        print_test("Alpha Vantage Key")
        print_warning("Not configured")
        record_result("Alpha Vantage", "warn", "No API key")
        return
    
    print_test("Alpha Vantage Key")
    print_success(f"{api_key[:10]}...")
    
    print_test("Alpha Vantage Connection")
    try:
        response = requests.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": "AAPL",
                "apikey": api_key
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'Global Quote' in data:
                quote = data['Global Quote']
                print_success()
                print_info("Symbol", quote.get('01. symbol'))
                print_info("Price", quote.get('05. price'))
                record_result("Alpha Vantage", "pass")
            else:
                print_warning("Rate limit or invalid response")
                record_result("Alpha Vantage", "warn", "Rate limit")
        else:
            print_failure(f"Status {response.status_code}")
            record_result("Alpha Vantage", "fail", f"Status {response.status_code}")
    except Exception as e:
        print_failure(str(e))
        record_result("Alpha Vantage", "fail", str(e))

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = results['passed'] + results['failed'] + results['warnings']
    
    print(f"{Colors.GREEN}Passed:   {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed:   {results['failed']}{Colors.END}")
    print(f"{Colors.YELLOW}Warnings: {results['warnings']}{Colors.END}")
    print(f"{Colors.CYAN}Total:    {total}{Colors.END}")
    
    if total > 0:
        success_rate = (results['passed'] / total) * 100
        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.END}")
    
    # Detailed results
    print(f"\n{Colors.CYAN}{'='*70}")
    print("DETAILED RESULTS")
    print(f"{'='*70}{Colors.END}\n")
    
    for test in results['tests']:
        status_color = Colors.GREEN if test['status'] == 'pass' else Colors.RED if test['status'] == 'fail' else Colors.YELLOW
        status_symbol = '✓' if test['status'] == 'pass' else '✗' if test['status'] == 'fail' else '⚠'
        print(f"{status_color}[{status_symbol}]{Colors.END} {test['name']}", end="")
        if test['details']:
            print(f" - {test['details']}")
        else:
            print()
    
    # Recommendations
    print(f"\n{Colors.CYAN}{'='*70}")
    print("RECOMMENDATIONS")
    print(f"{'='*70}{Colors.END}\n")
    
    if results['failed'] > 0:
        print(f"{Colors.RED}⚠ Some tests failed:{Colors.END}")
        print("  • Check if backend server is running")
        print("  • Verify API keys in backend/.env")
        print("  • Check network connectivity")
    
    if results['warnings'] > 0:
        print(f"\n{Colors.YELLOW}⚠ Some warnings:{Colors.END}")
        print("  • yfinance may be rate-limited (external API)")
        print("  • Grok API needs credits at https://console.x.ai")
        print("  • NewsAPI may need valid key")
    
    if results['passed'] == total:
        print(f"\n{Colors.GREEN}✓ All tests passed! System is fully operational.{Colors.END}")

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}")
    print("MARKETSHIELD AI - COMPREHENSIVE API TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}{Colors.END}\n")
    
    # Wait for server
    print(f"{Colors.YELLOW}Checking if backend server is ready...{Colors.END}")
    time.sleep(2)
    
    # Backend API Tests
    if test_backend_health():
        test_headline_analysis()
        test_company_search()
        test_market_data()
        test_news_endpoint()
    else:
        print(f"\n{Colors.RED}Backend server is not running. Skipping backend tests.{Colors.END}")
        print(f"{Colors.YELLOW}Start backend: cd backend && python -m uvicorn app.main:app --reload{Colors.END}\n")
    
    # External API Tests
    test_grok_api()
    test_newsapi()
    test_alpha_vantage()
    
    # Summary
    print_summary()
    
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}{Colors.END}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user.{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.END}")
