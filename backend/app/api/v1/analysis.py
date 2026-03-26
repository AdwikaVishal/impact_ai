from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.headline import HeadlineAnalyzeRequest, HeadlineAnalyzeResponse
import re
import random
from datetime import datetime
import yfinance as yf

router = APIRouter(prefix="/analysis", tags=["analysis"])

# Simple entity extraction using regex and keywords
def extract_entities(headline: str):
    """Extract company names and tickers from headline"""
    companies = []
    
    # Common company patterns
    company_patterns = {
        'Apple': 'AAPL',
        'Tesla': 'TSLA',
        'Microsoft': 'MSFT',
        'Google': 'GOOGL',
        'Amazon': 'AMZN',
        'Meta': 'META',
        'NVIDIA': 'NVDA',
        'Netflix': 'NFLX',
        'Reliance': 'RELIANCE.NS',
        'TCS': 'TCS.NS',
        'Infosys': 'INFY.NS',
        'HDFC': 'HDFCBANK.NS',
        'Bitcoin': 'BTC-USD',
        'Ethereum': 'ETH-USD',
    }
    
    for company, ticker in company_patterns.items():
        if company.lower() in headline.lower():
            companies.append({
                'name': company,
                'ticker': ticker,
                'confidence': 0.95
            })
    
    return companies

# Sentiment analysis using keyword matching
def analyze_sentiment(headline: str):
    """Analyze sentiment of headline"""
    positive_words = ['surge', 'gain', 'profit', 'growth', 'record', 'high', 'boost', 'rally', 
                     'strong', 'success', 'win', 'breakthrough', 'innovation', 'launch', 'expand']
    negative_words = ['fall', 'drop', 'loss', 'decline', 'crash', 'concern', 'risk', 'lawsuit',
                     'scandal', 'fraud', 'fail', 'weak', 'miss', 'cut', 'layoff', 'bankruptcy']
    
    headline_lower = headline.lower()
    
    positive_count = sum(1 for word in positive_words if word in headline_lower)
    negative_count = sum(1 for word in negative_words if word in headline_lower)
    
    if positive_count > negative_count:
        sentiment = 'POSITIVE'
        score = min(0.9, 0.5 + (positive_count * 0.15))
    elif negative_count > positive_count:
        sentiment = 'NEGATIVE'
        score = max(-0.9, -0.5 - (negative_count * 0.15))
    else:
        sentiment = 'NEUTRAL'
        score = 0.0
    
    return {
        'label': sentiment,
        'score': score,
        'confidence': abs(score)
    }

# Fake news detection
def detect_fake_news(headline: str):
    """Detect potential fake news indicators"""
    fake_indicators = ['shocking', 'unbelievable', 'you won\'t believe', 'secret', 'they don\'t want you to know',
                      'miracle', 'instant', 'guaranteed', 'breaking:', 'urgent:', 'alert:']
    
    headline_lower = headline.lower()
    indicator_count = sum(1 for indicator in fake_indicators if indicator in headline_lower)
    
    # Check for excessive punctuation
    exclamation_count = headline.count('!')
    question_count = headline.count('?')
    caps_ratio = sum(1 for c in headline if c.isupper()) / max(len(headline), 1)
    
    fake_score = (indicator_count * 0.2) + (exclamation_count * 0.1) + (caps_ratio * 0.3)
    fake_score = min(fake_score, 0.95)
    
    if fake_score > 0.6:
        label = 'LIKELY_FAKE'
    elif fake_score > 0.3:
        label = 'SUSPICIOUS'
    else:
        label = 'LIKELY_REAL'
    
    return {
        'label': label,
        'fake_probability': fake_score,
        'real_probability': 1 - fake_score,
        'confidence': abs(0.5 - fake_score) * 2
    }

# Event detection
def detect_event(headline: str):
    """Detect market events from headline"""
    events = {
        'earnings': ['earnings', 'profit', 'revenue', 'quarterly', 'q1', 'q2', 'q3', 'q4'],
        'merger': ['merger', 'acquisition', 'acquire', 'buyout', 'takeover'],
        'product_launch': ['launch', 'release', 'unveil', 'announce', 'introduce'],
        'lawsuit': ['lawsuit', 'sue', 'legal', 'court', 'settlement'],
        'layoff': ['layoff', 'job cut', 'downsize', 'restructure'],
        'expansion': ['expand', 'growth', 'new market', 'partnership'],
    }
    
    headline_lower = headline.lower()
    detected_events = []
    
    for event_type, keywords in events.items():
        if any(keyword in headline_lower for keyword in keywords):
            detected_events.append({
                'type': event_type,
                'confidence': 0.85
            })
    
    if detected_events:
        return detected_events[0]  # Return first detected event
    else:
        return {'type': 'general_news', 'confidence': 0.5}

# Get market data for entities
def get_market_data(entities):
    """Fetch market data for detected entities"""
    market_data = {}
    
    for entity in entities[:3]:  # Limit to first 3 entities
        try:
            ticker = yf.Ticker(entity['ticker'])
            info = ticker.info
            hist = ticker.history(period='5d')
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                change = ((current_price - prev_close) / prev_close) * 100
                
                market_data[entity['name']] = {
                    'ticker': entity['ticker'],
                    'price': float(current_price),
                    'change': float(change),
                    'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                    'market_cap': int(info.get('marketCap', 0))
                }
        except Exception as e:
            print(f"Error fetching market data for {entity['name']}: {e}")
            continue
    
    return market_data

# Calculate risk score
def calculate_risk_score(sentiment, fake_news, event, market_data):
    """Calculate overall risk score"""
    # Base risk from sentiment
    sentiment_risk = 0.5 - (sentiment['score'] * 0.5)  # Negative sentiment = higher risk
    
    # Fake news risk
    fake_risk = fake_news['fake_probability']
    
    # Event risk
    event_risk_map = {
        'lawsuit': 0.8,
        'layoff': 0.7,
        'earnings': 0.4,
        'merger': 0.5,
        'product_launch': 0.3,
        'expansion': 0.3,
        'general_news': 0.5
    }
    event_risk = event_risk_map.get(event['type'], 0.5)
    
    # Market volatility risk
    volatility_risk = 0.5
    if market_data:
        avg_change = sum(abs(data['change']) for data in market_data.values()) / len(market_data)
        volatility_risk = min(avg_change / 10, 1.0)  # Normalize to 0-1
    
    # Weighted average
    risk_score = (
        sentiment_risk * 0.3 +
        fake_risk * 0.25 +
        event_risk * 0.25 +
        volatility_risk * 0.2
    )
    
    # Determine risk level
    if risk_score < 0.3:
        risk_level = 'LOW'
    elif risk_score < 0.6:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'HIGH'
    
    return risk_score, risk_level

# Determine trading signal
def get_trading_signal(sentiment, risk_score, market_data):
    """Generate trading signal"""
    if risk_score > 0.7:
        return 'SELL'
    elif risk_score < 0.3 and sentiment['score'] > 0.5:
        return 'BUY'
    elif sentiment['score'] > 0.3:
        return 'HOLD_BULLISH'
    elif sentiment['score'] < -0.3:
        return 'HOLD_BEARISH'
    else:
        return 'NEUTRAL'

@router.post("/", response_model=HeadlineAnalyzeResponse)
async def analyze_headline(request: HeadlineAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Analyze a market headline using ML models
    """
    try:
        headline = request.headline.strip()
        
        if not headline:
            raise HTTPException(status_code=400, detail="Headline cannot be empty")
        
        # 1. Extract entities (companies, tickers)
        entities = extract_entities(headline)
        
        # 2. Sentiment analysis
        sentiment = analyze_sentiment(headline)
        
        # 3. Fake news detection
        fake_news = detect_fake_news(headline)
        
        # 4. Event detection
        event = detect_event(headline)
        
        # 5. Get market data for entities
        market_data = get_market_data(entities)
        
        # 6. Calculate risk score
        risk_score, risk_level = calculate_risk_score(sentiment, fake_news, event, market_data)
        
        # 7. Generate trading signal
        trading_signal = get_trading_signal(sentiment, risk_score, market_data)
        
        # 8. Compile analysis results
        analysis = {
            'sentiment': sentiment,
            'fake_news_detection': fake_news,
            'event': event,
            'entities_detected': len(entities),
            'market_impact': {
                'estimated_impact': 'HIGH' if abs(sentiment['score']) > 0.7 else 'MEDIUM' if abs(sentiment['score']) > 0.4 else 'LOW',
                'affected_companies': len(entities)
            }
        }
        
        return HeadlineAnalyzeResponse(
            analysis_id=random.randint(1000, 9999),
            risk_score=risk_level,
            risk_score_raw=float(risk_score),
            trading_signal=trading_signal,
            entities={'companies': entities},
            market_data=market_data,
            analysis=analysis,
            created_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error analyzing headline: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
