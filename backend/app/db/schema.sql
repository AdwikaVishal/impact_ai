-- MarketShield PostgreSQL Schema (exact spec)
-- Run: psql -f schema.sql marketshield

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE headlines (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    raw_headline TEXT NOT NULL,
    normalized_headline TEXT,
    entities JSONB,
    risk_score VARCHAR(10) NOT NULL,
    risk_score_raw DECIMAL(3,2),
    analysis JSONB NOT NULL,
    trading_signal VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_risk_score (risk_score),
    INDEX idx_created_at (created_at),
    INDEX idx_user_id (user_id)
);

CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    headline_id INTEGER REFERENCES headlines(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    current_price DECIMAL(15,4),
    price_change_pct DECIMAL(5,2),
    volume BIGINT,
    volatility DECIMAL(5,3),
    volume_spike BOOLEAN,
    data_snapshot JSONB,
    fetched_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(headline_id, symbol)
);

CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    headline_id INTEGER REFERENCES headlines(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    prediction_1d DECIMAL(15,4),
    prediction_5d DECIMAL(15,4),
    prediction_10d DECIMAL(15,4),
    confidence DECIMAL(3,2),
    prediction_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE news_feeds (
    id SERIAL PRIMARY KEY,
    headline_id INTEGER REFERENCES headlines(id),
    source VARCHAR(100),
    title TEXT,
    url TEXT,
    sentiment_score DECIMAL(3,2),
    published_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    service VARCHAR(50),
    api_key_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE realtime_updates (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    latest_price DECIMAL(15,4),
    updated_at TIMESTAMP DEFAULT NOW()
);

