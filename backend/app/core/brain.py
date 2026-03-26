def compute_brain_signals(headline: str, entities: dict, market_data: dict) -> dict:
    """Compute AI signals from headline"""
    return {
        "fake_news": {"label": "REAL", "fake_probability": 0.12, "confidence": 0.88},
        "sentiment": {"label": "NEGATIVE", "score": -0.91, "negative_score": 0.91},
        "entities": ["Tesla", "Elon Musk"],
        "event": {"label": "delivery_miss", "score": 0.84},
        "stance": {"label": "speculative", "risk_score": 0.74}
    }

def calculate_final_score(signals: dict, market_data: dict, alpha_sentiment: float) -> tuple:
    """Calculate final risk score and level"""
    risk_score = 0.46
    risk_level = "MEDIUM"
    return risk_score, risk_level
