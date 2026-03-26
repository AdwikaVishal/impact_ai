"""SQLAlchemy ORM models matching schema.sql"""
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    api_key = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Headline(Base):
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

# Add other models: MarketData, Prediction, NewsFeed, APIKey, RealtimeUpdate...
# (abbreviated for initial setup)

