from fastapi import APIRouter, HTTPException, Query
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional
import requests
import numpy as np

router = APIRouter(prefix="/market", tags=["market"])

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

def convert_symbol(symbol: str) -> str:
    """Convert TradingView symbol to Yahoo Finance symbol"""
    if symbol in SYMBOL_MAP:
        return SYMBOL_MAP[symbol]
    
    # Handle generic conversion
    if ':' in symbol:
        exchange, ticker = symbol.split(':')
        if exchange == 'NSE':
            return f"{ticker}.NS"
        elif exchange == 'BSE':
            return f"{ticker}.BO"
        elif exchange in ['NASDAQ', 'NYSE']:
            return ticker
    
    return symbol

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
    """Get real-time market data for a symbol"""
    try:
        # Convert symbol
        yf_symbol = convert_symbol(symbol)
        
        # Fetch data from yfinance
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info
        hist = ticker.history(period="5d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No data found for symbol")
        
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
        prediction = calculate_7day_prediction(ticker, float(current_price))
        
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "name": info.get('longName', info.get('shortName', symbol)),
                "ticker": symbol.split(':')[1] if ':' in symbol else symbol,
                "exchange": symbol.split(':')[0] if ':' in symbol else 'UNKNOWN',
                "price": float(current_price),
                "previousClose": float(previous_close),
                "change": float(change),
                "changePercent": float(change_percent),
                "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                "avgVolume": int(hist['Volume'].mean()) if 'Volume' in hist.columns else 0,
                "marketCap": int(info.get('marketCap', 0)),
                "currency": info.get('currency', 'USD'),
                "volatility": float(volatility),
                "high": float(hist['High'].iloc[-1]) if 'High' in hist.columns else float(current_price),
                "low": float(hist['Low'].iloc[-1]) if 'Low' in hist.columns else float(current_price),
                "timestamp": datetime.now().isoformat(),
                "prediction": prediction
            }
        }
    except Exception as e:
        print(f"Error fetching market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{symbol}/news")
async def get_company_news(symbol: str):
    """Get recent news for a company"""
    try:
        # Convert symbol
        yf_symbol = convert_symbol(symbol)
        
        # Fetch news from yfinance
        ticker = yf.Ticker(yf_symbol)
        news = ticker.news
        
        formatted_news = []
        # Just return all available news (yfinance already limits to recent news)
        for item in news:
            try:
                # News data is nested in 'content' object
                content = item.get('content', {})
                
                # Get publication date
                pub_date_str = content.get('pubDate', '')
                if pub_date_str:
                    # Parse ISO format date
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                else:
                    pub_date = datetime.now()
                
                # Get thumbnail URL
                thumbnail_url = ''
                thumbnail = content.get('thumbnail', {})
                if thumbnail and 'resolutions' in thumbnail and len(thumbnail['resolutions']) > 0:
                    thumbnail_url = thumbnail['resolutions'][0].get('url', '')
                
                # Get provider info
                provider = content.get('provider', {})
                publisher = provider.get('displayName', 'Unknown')
                
                # Get canonical URL
                canonical = content.get('canonicalUrl', {})
                link = canonical.get('url', '#')
                
                formatted_news.append({
                    "title": content.get('title', 'No title'),
                    "publisher": publisher,
                    "link": link,
                    "publishedAt": pub_date.isoformat(),
                    "thumbnail": thumbnail_url,
                    "summary": content.get('summary', '')
                })
            except Exception as item_error:
                print(f"Error processing news item: {item_error}")
                continue
        
        return {
            "success": True,
            "data": formatted_news
        }
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return {
            "success": True,
            "data": []
        }
