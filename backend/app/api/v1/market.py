from fastapi import APIRouter, HTTPException, Query
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional
import requests
import numpy as np
import os
from functools import lru_cache

router = APIRouter(prefix="/market", tags=["market"])

# API Keys - loaded by main.py
ALPHA_VANTAGE_KEY = None
NEWSAPI_KEY = None
GNEWS_API_KEY = None

def get_api_keys():
    """Get API keys from environment (loaded by main.py)"""
    global ALPHA_VANTAGE_KEY, NEWSAPI_KEY, GNEWS_API_KEY
    if ALPHA_VANTAGE_KEY is None:
        ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
        NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
        GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
    return ALPHA_VANTAGE_KEY, NEWSAPI_KEY, GNEWS_API_KEY

# Simple in-memory cache for news (5 minute TTL)
news_cache = {}
CACHE_TTL = 300  # 5 minutes

# Fallback sample news for when GNews fails
SAMPLE_NEWS = {
    "AAPL": [
        {"title": "Apple announces new AI features for iPhone", "publisher": "TechCrunch", "url": "https://techcrunch.com", "date": "2026-05-01"},
        {"title": "Apple stock reaches new highs on strong earnings", "publisher": "CNBC", "url": "https://cnbc.com", "date": "2026-05-01"},
    ],
    "TSLA": [
        {"title": "Tesla unveils next-generation electric vehicle", "publisher": "Reuters", "url": "https://reuters.com", "date": "2026-05-01"},
        {"title": "Tesla expands production capacity globally", "publisher": "Bloomberg", "url": "https://bloomberg.com", "date": "2026-05-01"},
    ],
    "MSFT": [
        {"title": "Microsoft Azure sees record growth", "publisher": "The Verge", "url": "https://theverge.com", "date": "2026-05-01"},
        {"title": "Microsoft announces new AI partnerships", "publisher": "TechCrunch", "url": "https://techcrunch.com", "date": "2026-05-01"},
    ],
    "NVDA": [
        {"title": "NVIDIA launches new AI chip series", "publisher": "AnandTech", "url": "https://anandtech.com", "date": "2026-05-01"},
        {"title": "NVIDIA stock surges on AI demand", "publisher": "MarketWatch", "url": "https://marketwatch.com", "date": "2026-05-01"},
    ],
}

# Symbol mapping for various assets
SYMBOL_MAP = {
    # Indian Indices
    'NSE:NIFTY': '^NSEI',
    'BSE:SENSEX': '^BSESN',
    # Indian Stocks
    'NSE:RELIANCE': 'RELIANCE.NS',
    'NSE:TCS': 'TCS.NS',
    'NSE:HDFCBANK': 'HDFCBANK.NS',
    'NSE:INFY': 'INFY.NS',
    'NSE:ITC': 'ITC.NS',
    'NSE:BHARTIARTL': 'BHARTIARTL.NS',
    'NSE:SBIN': 'SBIN.NS',
    'NSE:LT': 'LT.NS',
    'NSE:ICICIBANK': 'ICICIBANK.NS',
    'NSE:HINDUNILVR': 'HINDUNILVR.NS',
    'NSE:KOTAKBANK': 'KOTAKBANK.NS',
    'NSE:AXISBANK': 'AXISBANK.NS',
    'NSE:WIPRO': 'WIPRO.NS',
    'NSE:MARUTI': 'MARUTI.NS',
    'NSE:TATAMOTORS': 'TATAMOTORS.NS',
    'NSE:BAJFINANCE': 'BAJFINANCE.NS',
    'NSE:ASIANPAINT': 'ASIANPAINT.NS',
    'NSE:SUNPHARMA': 'SUNPHARMA.NS',
    # US Stocks
    'NASDAQ:TSLA': 'TSLA',
    'NASDAQ:AAPL': 'AAPL',
    'NASDAQ:MSFT': 'MSFT',
    'NASDAQ:NVDA': 'NVDA',
    'NASDAQ:GOOGL': 'GOOGL',
    'NASDAQ:AMZN': 'AMZN',
    'NASDAQ:META': 'META',
    'NYSE:JPM': 'JPM',
    'NYSE:V': 'V',
    'NYSE:WMT': 'WMT',
    # Commodities (Futures)
    'GC=F': 'GC=F',  # Gold
    'SI=F': 'SI=F',  # Silver
    'CL=F': 'CL=F',  # Crude Oil
    'NG=F': 'NG=F',  # Natural Gas
    'HG=F': 'HG=F',  # Copper
    # Cryptocurrencies
    'BTC-USD': 'BTC-USD',
    'ETH-USD': 'ETH-USD',
    'BNB-USD': 'BNB-USD',
}

def convert_symbol(symbol: str) -> tuple[str, str]:
    """Convert TradingView symbol to Yahoo Finance symbol and extract ticker"""
    yf_symbol = symbol
    ticker_only = symbol
    
    if symbol in SYMBOL_MAP:
        yf_symbol = SYMBOL_MAP[symbol]
        ticker_only = symbol.split(':')[1] if ':' in symbol else symbol
    elif ':' in symbol:
        exchange, ticker = symbol.split(':')
        ticker_only = ticker
        if exchange == 'NSE':
            yf_symbol = f"{ticker}.NS"
        elif exchange == 'BSE':
            yf_symbol = f"{ticker}.BO"
        elif exchange in ['NASDAQ', 'NYSE']:
            yf_symbol = ticker
    
    return yf_symbol, ticker_only

def get_alpha_vantage_data(symbol: str) -> dict:
    """Fetch data from Alpha Vantage as backup"""
    try:
        # Convert symbol to ticker only (Alpha Vantage doesn't use exchange prefix)
        _, ticker = convert_symbol(symbol)
        
        # Get quote data
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": ALPHA_VANTAGE_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "Global Quote" not in data or not data["Global Quote"]:
            return None
        
        quote = data["Global Quote"]
        
        # Parse Alpha Vantage response
        current_price = float(quote.get("05. price", 0))
        previous_close = float(quote.get("08. previous close", current_price))
        change = float(quote.get("09. change", 0))
        change_percent = float(quote.get("10. change percent", "0").replace("%", ""))
        volume = int(quote.get("06. volume", 0))
        high = float(quote.get("03. high", current_price))
        low = float(quote.get("04. low", current_price))
        
        return {
            "symbol": symbol,
            "name": ticker,
            "ticker": ticker,
            "exchange": symbol.split(':')[0] if ':' in symbol else 'UNKNOWN',
            "price": current_price,
            "previousClose": previous_close,
            "change": change,
            "changePercent": change_percent,
            "volume": volume,
            "avgVolume": volume,
            "marketCap": 0,
            "currency": "USD",
            "volatility": 0,
            "high": high,
            "low": low,
            "timestamp": datetime.now().isoformat(),
            "source": "alpha_vantage",
            "prediction": {
                "predicted_price": round(current_price * 1.015, 2),
                "confidence": 0.50,
                "change_percent": 1.5,
                "method": "fallback",
                "days": 7
            }
        }
    except Exception as e:
        print(f"Alpha Vantage error for {symbol}: {e}")
        return None

def calculate_7day_prediction(ticker_obj, current_price: float) -> dict:
    """Calculate 7-day price prediction using enhanced ML approach with multiple indicators"""
    try:
        # Get 90 days of historical data for more accurate prediction
        hist = ticker_obj.history(period="90d")
        
        if len(hist) < 7:
            # Fallback to simple growth estimate
            return {
                "predicted_price": round(current_price * 1.015, 2),
                "confidence": 0.45,
                "change_percent": 1.5,
                "method": "fallback"
            }
        
        # Calculate daily returns
        hist['returns'] = hist['Close'].pct_change()
        
        # Remove NaN values
        returns = hist['returns'].dropna()
        
        if len(returns) < 7:
            return {
                "predicted_price": round(current_price * 1.015, 2),
                "confidence": 0.45,
                "change_percent": 1.5,
                "method": "fallback"
            }
        
        # Calculate statistics
        mean_return = returns.mean()
        std_return = returns.std()
        
        # Calculate multiple timeframe trends
        prices = hist['Close'].values
        
        # Short-term trend (last 7 days)
        if len(prices) >= 7:
            short_prices = prices[-7:]
            short_x = np.arange(len(short_prices))
            short_slope = np.polyfit(short_x, short_prices, 1)[0]
            short_trend = short_slope / short_prices.mean()
        else:
            short_trend = 0
        
        # Medium-term trend (last 30 days)
        if len(prices) >= 30:
            med_prices = prices[-30:]
            med_x = np.arange(len(med_prices))
            med_slope = np.polyfit(med_x, med_prices, 1)[0]
            med_trend = med_slope / med_prices.mean()
        else:
            med_trend = short_trend
        
        # Calculate momentum indicators
        # RSI-like momentum (recent strength)
        if len(returns) >= 14:
            recent_returns = returns.iloc[-14:]
            gains = recent_returns[recent_returns > 0].sum()
            losses = abs(recent_returns[recent_returns < 0].sum())
            if losses != 0:
                rs = gains / losses
                rsi = 100 - (100 / (1 + rs))
                momentum_factor = (rsi - 50) / 100  # Normalize to -0.5 to 0.5
            else:
                momentum_factor = 0.5 if gains > 0 else 0
        else:
            momentum_factor = 0
        
        # Volume trend (if available)
        volume_factor = 0
        if 'Volume' in hist.columns and len(hist) >= 7:
            recent_vol = hist['Volume'].iloc[-7:].mean()
            avg_vol = hist['Volume'].mean()
            if avg_vol > 0:
                volume_factor = (recent_vol - avg_vol) / avg_vol
                volume_factor = np.clip(volume_factor, -0.3, 0.3)  # Limit impact
        
        # Calculate support and resistance levels
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        price_position = (current_price - low_52w) / (high_52w - low_52w) if high_52w != low_52w else 0.5
        
        # Resistance factor (closer to high = more resistance)
        resistance_factor = -0.1 * (price_position - 0.5) if price_position > 0.7 else 0
        
        # Enhanced weighted prediction for 7 days
        # Weights: 35% short-term trend, 25% medium-term trend, 20% momentum, 
        #          10% mean return, 5% volume, 5% resistance
        expected_return = (
            0.35 * short_trend * 7 +           # Short-term trend (most important for 7 days)
            0.25 * med_trend * 7 +             # Medium-term trend
            0.20 * momentum_factor * 0.07 +    # Momentum indicator
            0.10 * mean_return * 7 +           # Historical mean return
            0.05 * volume_factor * 0.05 +      # Volume trend
            0.05 * resistance_factor           # Support/resistance
        )
        
        # Apply volatility adjustment (reduce extreme predictions)
        volatility_adjustment = 1 - (std_return * 3)
        volatility_adjustment = np.clip(volatility_adjustment, 0.5, 1.0)
        expected_return *= volatility_adjustment
        
        # Calculate predicted price
        predicted_price = current_price * (1 + expected_return)
        
        # Enhanced confidence calculation
        # Higher confidence for: lower volatility, consistent trends, higher volume
        base_confidence = 0.65
        
        # Volatility impact (lower vol = higher confidence)
        vol_confidence = max(0, 0.25 - (std_return * 15))
        
        # Trend consistency (aligned short and medium trends = higher confidence)
        trend_alignment = 1 - abs(short_trend - med_trend) * 10
        trend_confidence = max(0, min(0.15, trend_alignment * 0.15))
        
        # Data quality (more data = higher confidence)
        data_confidence = min(0.10, len(hist) / 900)  # Max at 90 days
        
        confidence = base_confidence + vol_confidence + trend_confidence + data_confidence
        confidence = np.clip(confidence, 0.40, 0.95)
        
        # Calculate change percentage
        change_percent = ((predicted_price - current_price) / current_price) * 100
        
        return {
            "predicted_price": round(float(predicted_price), 2),
            "confidence": round(float(confidence), 2),
            "change_percent": round(float(change_percent), 2),
            "method": "ml_enhanced",
            "volatility": round(float(std_return), 4),
            "trend_strength": round(float(abs(short_trend) * 100), 2),
            "momentum": round(float(momentum_factor * 100), 2),
            "days": 7
        }
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        import traceback
        traceback.print_exc()
        # Fallback prediction
        return {
            "predicted_price": round(current_price * 1.015, 2),
            "confidence": 0.45,
            "change_percent": 1.5,
            "method": "fallback",
            "days": 7
        }

@router.get("/search")
async def search_companies(q: str = Query(..., min_length=1)):
    """Search for any ticker: stocks, ETFs, commodities, bonds, crypto, etc."""
    try:
        results = []
        
        # Try to search using yfinance Ticker (works for most symbols)
        try:
            # Direct ticker lookup
            ticker = yf.Ticker(q.upper())
            info = ticker.info
            
            # If we got valid info, add it
            if info and info.get('symbol'):
                symbol = info.get('symbol', q.upper())
                exchange = info.get('exchange', 'UNKNOWN')
                
                # Map exchange to our format
                if exchange in ['NSI', 'NSE']:
                    formatted_symbol = f"NSE:{symbol}"
                elif exchange in ['BSE', 'BOM']:
                    formatted_symbol = f"BSE:{symbol}"
                elif exchange in ['NMS', 'NAS', 'NASDAQ']:
                    formatted_symbol = f"NASDAQ:{symbol}"
                elif exchange in ['NYQ', 'NYSE']:
                    formatted_symbol = f"NYSE:{symbol}"
                else:
                    formatted_symbol = f"{exchange}:{symbol}" if exchange != 'UNKNOWN' else symbol
                
                results.append({
                    "symbol": formatted_symbol,
                    "name": info.get('longName', info.get('shortName', symbol)),
                    "exchange": exchange,
                    "type": info.get('quoteType', 'EQUITY')
                })
        except:
            pass
        
        # Add popular companies as suggestions (always show these)
        popular_companies = [
            {"symbol": "NSE:NIFTY", "name": "NIFTY 50", "exchange": "NSE", "type": "INDEX"},
            {"symbol": "BSE:SENSEX", "name": "SENSEX", "exchange": "BSE", "type": "INDEX"},
            {"symbol": "NSE:RELIANCE", "name": "Reliance Industries", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:TCS", "name": "Tata Consultancy Services", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:HDFCBANK", "name": "HDFC Bank", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:INFY", "name": "Infosys", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:ITC", "name": "ITC Limited", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:BHARTIARTL", "name": "Bharti Airtel", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:SBIN", "name": "State Bank of India", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:LT", "name": "Larsen & Toubro", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:ICICIBANK", "name": "ICICI Bank", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:HINDUNILVR", "name": "Hindustan Unilever", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:KOTAKBANK", "name": "Kotak Mahindra Bank", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:AXISBANK", "name": "Axis Bank", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:WIPRO", "name": "Wipro", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:MARUTI", "name": "Maruti Suzuki", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:TATAMOTORS", "name": "Tata Motors", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:BAJFINANCE", "name": "Bajaj Finance", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:ASIANPAINT", "name": "Asian Paints", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NSE:SUNPHARMA", "name": "Sun Pharmaceutical", "exchange": "NSE", "type": "EQUITY"},
            {"symbol": "NASDAQ:TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
            {"symbol": "NASDAQ:AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
            {"symbol": "NASDAQ:MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "type": "EQUITY"},
            {"symbol": "NASDAQ:NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "type": "EQUITY"},
            {"symbol": "NASDAQ:GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
            {"symbol": "NASDAQ:AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
            {"symbol": "NASDAQ:META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
            {"symbol": "NYSE:JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE", "type": "EQUITY"},
            {"symbol": "NYSE:V", "name": "Visa Inc.", "exchange": "NYSE", "type": "EQUITY"},
            {"symbol": "NYSE:WMT", "name": "Walmart Inc.", "exchange": "NYSE", "type": "EQUITY"},
            # Commodities
            {"symbol": "GC=F", "name": "Gold Futures", "exchange": "COMEX", "type": "COMMODITY"},
            {"symbol": "SI=F", "name": "Silver Futures", "exchange": "COMEX", "type": "COMMODITY"},
            {"symbol": "CL=F", "name": "Crude Oil Futures", "exchange": "NYMEX", "type": "COMMODITY"},
            {"symbol": "BTC-USD", "name": "Bitcoin USD", "exchange": "CRYPTO", "type": "CRYPTOCURRENCY"},
            {"symbol": "ETH-USD", "name": "Ethereum USD", "exchange": "CRYPTO", "type": "CRYPTOCURRENCY"},
        ]
        
        # Filter based on query
        query_lower = q.lower()
        filtered = [
            comp for comp in popular_companies 
            if query_lower in comp['name'].lower() or 
               query_lower in comp['symbol'].lower() or
               query_lower in comp.get('type', '').lower()
        ]
        
        # Combine results (direct match first, then filtered popular)
        all_results = results + filtered
        
        # Remove duplicates based on symbol
        seen = set()
        unique_results = []
        for item in all_results:
            if item['symbol'] not in seen:
                seen.add(item['symbol'])
                unique_results.append(item)
        
        return {
            "success": True,
            "data": unique_results[:15]  # Limit to 15 results
        }
    except Exception as e:
        print(f"Error searching companies: {e}")
        import traceback
        traceback.print_exc()
        return {"success": True, "data": []}

@router.get("/{symbol}")
async def get_market_data(symbol: str):
    """Get real-time market data for a symbol with Alpha Vantage backup"""
    try:
        # Convert symbol
        yf_symbol, ticker = convert_symbol(symbol)
        
        # Try yfinance first
        try:
            ticker_obj = yf.Ticker(yf_symbol)
            
            # Try different periods if one fails
            hist = None
            for period in ["1d", "5d", "1mo"]:
                try:
                    hist = ticker_obj.history(period=period)
                    if not hist.empty:
                        break
                except:
                    continue
            
            if hist is not None and not hist.empty:
                # Get info with error handling
                try:
                    info = ticker_obj.info
                except:
                    info = {}
                
                current_price = hist['Close'].iloc[-1]
                previous_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price)
                
                # Calculate change
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close else 0
                
                # Calculate volatility (standard deviation of returns)
                if len(hist) > 1:
                    returns = hist['Close'].pct_change().dropna()
                    volatility = returns.std() * 100  # Convert to percentage
                else:
                    volatility = 0
                
                # Calculate 7-day prediction using enhanced ML
                prediction = calculate_7day_prediction(ticker_obj, float(current_price))
                
                return {
                    "success": True,
                    "data": {
                        "symbol": symbol,
                        "name": info.get('longName', info.get('shortName', symbol)),
                        "ticker": ticker,
                        "exchange": symbol.split(':')[0] if ':' in symbol else 'UNKNOWN',
                        "price": float(current_price),
                        "previousClose": float(previous_close),
                        "change": float(change),
                        "changePercent": float(change_percent),
                        "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns and len(hist) > 0 else 0,
                        "avgVolume": int(hist['Volume'].mean()) if 'Volume' in hist.columns and len(hist) > 0 else 0,
                        "marketCap": int(info.get('marketCap', 0)) if info.get('marketCap') else 0,
                        "currency": info.get('currency', 'USD'),
                        "volatility": float(volatility),
                        "high": float(hist['High'].iloc[-1]) if 'High' in hist.columns and len(hist) > 0 else float(current_price),
                        "low": float(hist['Low'].iloc[-1]) if 'Low' in hist.columns and len(hist) > 0 else float(current_price),
                        "timestamp": datetime.now().isoformat(),
                        "source": "yfinance",
                        "prediction": prediction
                    }
                }
        except Exception as yf_error:
            print(f"yfinance failed for {symbol}: {yf_error}")
            # Fall through to Alpha Vantage
        
        # Try Alpha Vantage as backup
        ALPHA_VANTAGE_KEY, _, _ = get_api_keys()
        if ALPHA_VANTAGE_KEY:
            print(f"Trying Alpha Vantage for {symbol}...")
            av_data = get_alpha_vantage_data(symbol)
            if av_data:
                return {
                    "success": True,
                    "data": av_data
                }
        
        # If both fail, return error
        raise HTTPException(status_code=404, detail=f"No data available for symbol {symbol}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching market data for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")

@router.get("/{symbol}/news")
async def get_company_news(symbol: str):
    """Get recent news for a company using GNews.io API"""
    try:
        # Get API keys
        _, _, GNEWS_API_KEY = get_api_keys()
        
        # Check cache first
        cache_key = f"news_{symbol}"
        if cache_key in news_cache:
            cached_data, cached_time = news_cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < CACHE_TTL:
                print(f"✅ Returning cached news for {symbol}")
                return cached_data
        
        # Convert symbol to ticker
        _, ticker = convert_symbol(symbol)
        
        formatted_news = []
        
        # Use GNews.io API (fast, reliable, with API key)
        if GNEWS_API_KEY:
            try:
                print(f"Fetching news from GNews.io API for: {ticker}")
                
                # GNews.io API endpoint
                url = "https://gnews.io/api/v4/search"
                params = {
                    "q": ticker,
                    "apikey": GNEWS_API_KEY,  # Changed from 'token' to 'apikey'
                    "lang": "en",
                    "max": 10,
                    "sortby": "publishedAt"
                }
                
                response = requests.get(url, params=params, timeout=5)
                print(f"GNews.io response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])
                    print(f"GNews.io returned {len(articles)} articles")
                    
                    for article in articles:
                        try:
                            formatted_news.append({
                                "title": article.get("title", "No title"),
                                "publisher": article.get("source", {}).get("name", "Unknown"),
                                "link": article.get("url", "#"),
                                "publishedAt": article.get("publishedAt", datetime.now().isoformat()),
                                "thumbnail": article.get("image", ""),
                                "summary": article.get("description", "")
                            })
                        except Exception as item_error:
                            print(f"Error processing GNews.io item: {item_error}")
                            continue
                    
                    if formatted_news:
                        print(f"✅ GNews.io returned {len(formatted_news)} articles")
                        response_data = {
                            "success": True,
                            "data": formatted_news,
                            "source": "gnews.io"
                        }
                        # Cache the result
                        news_cache[cache_key] = (response_data, datetime.now())
                        return response_data
                else:
                    print(f"GNews.io API error: {response.status_code} - {response.text}")
            except Exception as gnews_error:
                print(f"GNews.io error for {symbol}: {gnews_error}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️  GNEWS_API_KEY not found in environment")
        
        # Fallback to sample news if GNews.io fails
        if ticker in SAMPLE_NEWS:
            print(f"📰 Using sample news for {ticker}")
            sample_articles = SAMPLE_NEWS[ticker]
            formatted_news = [
                {
                    "title": article["title"],
                    "publisher": article["publisher"],
                    "link": article["url"],
                    "publishedAt": datetime.now().isoformat(),
                    "thumbnail": "",
                    "summary": article["title"]
                }
                for article in sample_articles
            ]
            response_data = {
                "success": True,
                "data": formatted_news,
                "source": "sample"
            }
            # Cache sample data (shorter TTL)
            news_cache[cache_key] = (response_data, datetime.now() - timedelta(seconds=CACHE_TTL - 120))
            return response_data
        
        # Return empty array if everything fails
        print(f"⚠️  No news found for {symbol}")
        response_data = {
            "success": True,
            "data": [],
            "source": "none"
        }
        return response_data
        
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": True,
            "data": [],
            "source": "error"
        }
