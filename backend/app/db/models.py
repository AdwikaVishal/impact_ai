"""
SQLAlchemy ORM Models for Intelligence Data
Supports dual-write pattern: PostgreSQL + JSON fallback
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .session import Base


class User(Base):
    """User accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    api_key = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    intelligence_reports = relationship("IntelligenceReport", back_populates="user")


class IntelligenceReport(Base):
    """Stored intelligence reports"""
    __tablename__ = "intelligence_reports"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Company info
    company_name = Column(String(255), nullable=False)
    category = Column(String(255))
    
    # Intelligence data (stored as JSON)
    business_model = Column(Text)
    positioning = Column(Text)
    scale_metrics = Column(JSON)
    brand_perception = Column(Text)
    recent_shifts = Column(Text)
    competitors = Column(JSON)
    activities = Column(JSON)
    events = Column(JSON)
    watchouts = Column(JSON)
    decision_makers = Column(JSON)
    outreach_messages = Column(JSON)
    
    # Metadata
    confidence_score = Column(Numeric(3,2))
    generated_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="intelligence_reports")
    
    # Indexes
    __table_args__ = (
        Index("idx_company_name", "company_name"),
        Index("idx_created_at", "created_at"),
        Index("idx_user_id", "user_id"),
    )


class Headline(Base):
    """News headlines analysis"""
    __tablename__ = "headlines"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    raw_headline = Column(Text, nullable=False)
    normalized_headline = Column(Text)
    entities = Column(JSON)
    risk_score = Column(String(10), nullable=False)
    risk_score_raw = Column(Numeric(3,2))
    analysis = Column(JSON, nullable=False)
    trading_signal = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index("idx_risk_score", "risk_score"),
        Index("idx_created_at", "created_at"),
        Index("idx_user_id", "user_id"),
    )


class MarketData(Base):
    """Market data snapshots"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True)
    headline_id = Column(Integer, ForeignKey("headlines.id", ondelete="CASCADE"))
    symbol = Column(String(20), nullable=False)
    current_price = Column(Numeric(15,4))
    price_change_pct = Column(Numeric(5,2))
    volume = Column(Integer)
    volatility = Column(Numeric(5,3))
    volume_spike = Column(Boolean)
    data_snapshot = Column(JSON)
    fetched_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index("idx_symbol", "symbol"),
        Index("idx_headline_id", "headline_id"),
    )


class CacheEntry(Base):
    """Cache entries for persistence"""
    __tablename__ = "cache_entries"
    
    id = Column(Integer, primary_key=True)
    cache_key = Column(String(255), unique=True, nullable=False)
    cache_value = Column(JSON, nullable=False)
    ttl_seconds = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)
    
    __table_args__ = (
        Index("idx_cache_key", "cache_key"),
        Index("idx_expires_at", "expires_at"),
    )

