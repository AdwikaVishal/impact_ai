# MarketShield 🛡️

AI-powered financial news analysis and market intelligence platform. Detect fake news, analyze sentiment, assess risk, and get trading signals in real-time.

## Features

### 🎯 Headline Analyzer
- **Fake News Detection** - Multi-factor credibility analysis
- **Sentiment Analysis** - AI-powered mood scoring
- **Event Detection** - Identifies earnings, mergers, lawsuits, etc.
- **Risk Assessment** - Comprehensive risk scoring (0-100%)
- **Trading Signals** - BUY/SELL/HOLD recommendations
- **Price Charts** - 7-day historical price visualization

### 📊 Dashboard
- **Company Search** - Search stocks, crypto, commodities, bonds
- **Real-time Data** - Live prices, changes, volume, market cap
- **7-Day Prediction** - ML-powered price targets with confidence scores
- **News Feed** - Latest company news with sentiment indicators
- **Interactive Charts** - TradingView integration

### 📈 Market Overview
- **Major Indices** - S&P 500, Dow Jones, NASDAQ, Russell 2000
- **Sector Performance** - Technology, Healthcare, Finance, Energy, etc.
- **Interactive Details** - Click for in-depth information

### 📋 Watchlist
- **Asset Tracking** - Monitor your favorite stocks/crypto
- **Price Alerts** - Set notifications for price movements
- **Quick Actions** - Add/remove assets easily

## Tech Stack

**Backend:**
- FastAPI (Python)
- yfinance (Market Data)
- SQLAlchemy (Database)
- Pydantic (Validation)

**Frontend:**
- React 18
- Vite
- TailwindCSS
- Framer Motion
- Zustand (State Management)
- React Router

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd marketshield
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Frontend Setup**
```bash
cd marketshield-frontend
npm install
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## ML Models

### Headline Analysis Pipeline
1. **Entity Extraction** - Regex-based company/ticker detection
2. **Sentiment Analysis** - Keyword matching with confidence scoring
3. **Fake News Detection** - Clickbait indicators, punctuation analysis, caps ratio
4. **Event Detection** - Pattern matching for market events
5. **Market Data Fetch** - Real-time data via yfinance
6. **Risk Calculation** - Weighted formula (sentiment 30%, fake news 25%, event 25%, volatility 20%)
7. **Signal Generation** - Trading recommendations based on combined analysis

### Price Prediction
- Technical indicators: trend analysis, momentum, RSI-like scoring
- Confidence scoring based on volatility and data quality
- 7-day target price with percentage change

## Supported Assets

**Stocks:** AAPL, TSLA, MSFT, GOOGL, AMZN, META, NVDA, NFLX, RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS

**Crypto:** BTC-USD, ETH-USD

**Commodities:** GC=F (Gold), SI=F (Silver)

## API Endpoints

### Analysis
```
POST /api/v1/analysis/
Body: {"headline": "Your headline here"}
```

### Market Data
```
GET /api/v1/market/{symbol}
GET /api/v1/market/{symbol}/news
GET /api/v1/market/search?q={query}
```

## Project Structure

```
marketshield/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Business logic
│   │   ├── db/              # Database
│   │   └── main.py          # FastAPI app
│   └── requirements.txt
│
└── marketshield-frontend/
    ├── src/
    │   ├── components/      # React components
    │   ├── pages/           # Page components
    │   ├── hooks/           # Custom hooks
    │   ├── services/        # API services
    │   └── stores/          # State management
    └── package.json
```

## Screenshots

### Dashboard
Real-time company data with search, predictions, and news feed.

### Analyzer
AI-powered headline analysis with risk assessment and trading signals.

### Market Overview
Track major indices and sector performance.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Market data provided by yfinance
- Charts powered by TradingView
- UI components styled with TailwindCSS
- Animations by Framer Motion

## Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ for smarter financial decisions
