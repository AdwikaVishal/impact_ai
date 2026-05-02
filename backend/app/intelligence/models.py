"""
Data models for Market Intelligence Engine
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class CompanyInput(BaseModel):
    """Input for intelligence gathering"""
    company_name: str = Field(..., description="Company name")
    category: str = Field(..., description="One-line category/industry")


class Competitor(BaseModel):
    """Competitor information"""
    name: str
    domain: str
    relevance_score: float
    traffic_rank: Optional[int] = None
    strengths: List[str] = []
    weaknesses: List[str] = []


class DecisionMaker(BaseModel):
    """Decision maker profile"""
    name: str
    title: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    relevance_score: float


class BrandActivity(BaseModel):
    """Brand activity/campaign"""
    title: str
    description: str
    date: str
    activity_type: str  # campaign, launch, partnership, press
    source_url: str


class Event(BaseModel):
    """Company event"""
    name: str
    date: str
    event_type: str  # conference, activation, launch
    format: str  # virtual, in-person, hybrid
    estimated_scale: str  # small, medium, large


class Watchout(BaseModel):
    """Strategic watchout/risk"""
    risk_type: str  # market_sentiment, reputational, operational
    description: str
    severity: str  # low, medium, high


class OutreachMessage(BaseModel):
    """Generated outreach message"""
    channel: str  # email, linkedin
    subject: Optional[str] = None
    message: str
    personalization_notes: List[str]


class CompanyIntelligence(BaseModel):
    """Complete intelligence report"""
    company_name: str
    category: str
    
    # 1. Company Overview
    business_model: str
    positioning: str
    scale_metrics: Dict[str, Any]
    
    # 2. Market Position
    brand_perception: str
    recent_shifts: List[str]
    
    # 3. Competitor Mapping
    competitors: List[Competitor]
    
    # 4. Brand Activity
    activities: List[BrandActivity]
    
    # 5. Events Footprint
    events: List[Event]
    
    # 6. Strategic Watchouts
    watchouts: List[Watchout]
    
    # 7-8. Decision Makers & Contacts
    decision_makers: List[DecisionMaker]
    
    # 9. Personalized Outreach
    outreach_messages: Dict[str, OutreachMessage]
    
    # Metadata
    generated_at: datetime
    confidence_score: float
