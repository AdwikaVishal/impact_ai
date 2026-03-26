from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class HeadlineAnalyzeRequest(BaseModel):
    headline: str

class HeadlineAnalyzeResponse(BaseModel):
    analysis_id: int
    risk_score: str
    risk_score_raw: float
    trading_signal: str
    entities: Dict[str, Any]
    market_data: Dict[str, Any]
    analysis: Dict[str, Any]
    created_at: datetime
