# MarketShield - Running Guide

## Quick Start

### Backend (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend runs on: http://localhost:8000

### Frontend (React + Vite)
```bash
cd marketshield-frontend
npm run dev
```
Frontend runs on: http://localhost:5173

## Project Structure

```
marketshield/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API endpoints
│   │   │   ├── analysis.py    # ML headline analysis
│   │   │   └── market.py      # Market data & search
│   │   ├── core/              # Business logic
│   │   ├── db/                # Database models
│   │   └── main.py            # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
│
└── marketshield-frontend/     # React frontend
    ├── src/
    │   ├── components/        # Reusable components
    │   │   ├── analyzer/      # Headline analyzer
    │   │   └── dashboard/     # Dashboard components
    │   ├── pages/             # Main pages
    │   │   ├── Dashboard.jsx  # Main dashboard
    │   │   ├── Analyzer.jsx   # Headline analyzer
    │   │   ├── MarketOverview.jsx
    │   │   └── Watchlist.jsx
    │   ├── hooks/             # Custom React hooks
    │   ├── services/          # API services
    │   ├── stores/            # Zustand state management
    │   └── utils/             # Utility functions
    └── package.json
```

## Features

### 1. Dashboard
- Real-time company data with search
- 7-day price prediction using ML
- Latest news feed
- Interactive price charts
- Company metrics and analysis

### 2. Analyzer
- AI-powered headline analysis
- Fake news detection
- Sentiment analysis
- Event detection
- Risk assessment
- Trading signal generation
- 7-day price history chart

### 3. Market Overview
- Major indices tracking
- Sector performance
- Interactive modals with details

### 4. Watchlist
- Add/remove assets
- Price alerts
- Real-time updates

## API Endpoints

### Analysis
- `POST /api/v1/analysis/` - Analyze headline with ML models

### Market Data
- `GET /api/v1/market/{symbol}` - Get company data with 7-day prediction
- `GET /api/v1/market/{symbol}/news` - Get latest news
- `GET /api/v1/market/search?q={query}` - Search companies/assets

## ML Models

### Headline Analysis
1. **Entity Extraction** - Detects companies/tickers (14 supported)
2. **Sentiment Analysis** - Keyword-based sentiment scoring
3. **Fake News Detection** - Multi-factor credibility analysis
4. **Event Detection** - Identifies market events (earnings, mergers, etc.)
5. **Risk Scoring** - Weighted risk calculation
6. **Trading Signals** - BUY/SELL/HOLD recommendations

### Price Prediction
- 7-day target price using technical indicators
- Confidence scoring based on volatility
- Multiple factors: trend, momentum, RSI, volume

## Supported Assets

### Stocks
- AAPL, TSLA, MSFT, GOOGL, AMZN, META, NVDA, NFLX
- RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS

### Crypto
- BTC-USD, ETH-USD

### Commodities
- GC=F (Gold), SI=F (Silver)

## Tech Stack

### Backend
- FastAPI
- yfinance (market data)
- SQLAlchemy
- Pydantic

### Frontend
- React 18
- Vite
- TailwindCSS
- Framer Motion
- Zustand
- React Router

## Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./marketshield.db
ALPHA_VANTAGE_API_KEY=your_key_here
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Development

### Install Dependencies

Backend:
```bash
cd backend
pip install -r requirements.txt
```

Frontend:
```bash
cd marketshield-frontend
npm install
```

### Database Setup
```bash
cd backend
python -c "from app.db.session import init_db; init_db()"
```

## Troubleshooting

### CORS Issues
- Backend configured for http://localhost:5173
- Check CORS settings in backend/app/main.py

### Port Conflicts
- Backend: Change port in uvicorn command
- Frontend: Change port in vite.config.js

### API Connection
- Verify backend is running on port 8000
- Check VITE_API_URL in frontend .env

## Notes

- Backend must be running before frontend
- Market data requires internet connection
- Some features require API keys (Alpha Vantage)
- Historical data limited to available yfinance data
