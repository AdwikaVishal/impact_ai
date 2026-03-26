import requests
from alpha_vantage_client import get_alpha_news_sentiment
from event_analyzer import classify_event
from stance_detector import detect_stance
from scam_detector import get_scam_score   # ✅ NEW


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "phi3"


# ===============================
# NORMALIZERS
# ===============================

def normalize_fake_result(fake_result):
    item = fake_result[0]
    label = item["label"]
    score = float(item["score"])

    if label == "LABEL_0":
        predicted_label = "Fake"
        fake_probability = score
    else:
        predicted_label = "Real"
        fake_probability = 1 - score

    return {
        "predicted_label": predicted_label,
        "fake_probability": round(fake_probability, 4)
    }


def normalize_sentiment_result(sentiment_result):
    item = sentiment_result[0]
    label = str(item["label"]).lower()
    score = float(item["score"])

    negative_score = score if "negative" in label else 0.0

    return {
        "sentiment_label": label,
        "sentiment_score": round(score, 4),
        "negative_score": round(negative_score, 4)
    }


def extract_company(entities):
    for entity in entities:
        if entity.get("entity_group") == "ORG":
            return str(entity.get("word"))
    return "Unknown"


# ===============================
# SIGNAL ENGINE
# ===============================

def compute_brain_signals(headline, models, market_data, source_trust):

    fake_result = models["fake"](headline[:500])
    sentiment_result = models["sentiment"](headline[:500])

    fake_data = normalize_fake_result(fake_result)
    sentiment_data = normalize_sentiment_result(sentiment_result)

    event = classify_event(headline, models["event"])
    stance = detect_stance(headline, models["stance"])
    alpha_sentiment = get_alpha_news_sentiment(headline)

    # ✅ NEW
    scam_score = get_scam_score(headline)

    return {
        "fake_data": fake_data,
        "sentiment_data": sentiment_data,
        "event": event,
        "stance": stance,
        "alpha_sentiment": alpha_sentiment,
        "source_trust": round(source_trust, 4),
        "scam_score": scam_score   # ✅ added
    }


# ===============================
# FINAL RISK SCORING
# ===============================

def calculate_final_score(signals, market, rumor_score):

    fake_probability = signals["fake_data"]["fake_probability"]
    negative_score = signals["sentiment_data"]["negative_score"]
    source_risk = 1 - signals["source_trust"]
    stance_risk = signals["stance"]["stance_risk"]
    event_score = signals["event"]["event_score"]
    scam_score = signals.get("scam_score", 0.0)   # ✅ NEW

    market_impact = market.get("market_impact_score", 0.0)
    volatility = market.get("volatility", 0.0)
    volume_spike = market.get("volume_spike", 0.0)

    volume_component = min(volume_spike / 3, 1.0)

    alpha_component = 0.0
    if signals["alpha_sentiment"] < 0:
        alpha_component = min(abs(signals["alpha_sentiment"]), 1.0)

    # 🧠 FINAL COMBINED SCORE
    score = (
        0.20 * fake_probability +
        0.10 * negative_score +
        0.12 * market_impact +
        0.08 * volatility +
        0.08 * volume_component +
        0.10 * source_risk +
        0.10 * stance_risk +
        0.06 * event_score +
        0.06 * rumor_score +
        0.06 * alpha_component +
        0.08 * scam_score   # ✅ NEW SIGNAL
    )

    if score >= 0.7:
        level = "High"
    elif score >= 0.4:
        level = "Medium"
    else:
        level = "Low"

    return round(score, 4), level


# ===============================
# LLM BRAIN
# ===============================

def ask_llm_brain(full_data):

    system_prompt = """
You are a financial misinformation risk analyst.

You must use the provided rule-based risk level as the final risk level.
Do not change it.
Use only the facts and numbers given.
Do not invent values.

Return JSON only with:
risk_level
summary
reasoning
alert_message
"""

    prompt = f"""
Headline: {full_data['headline']}
Company: {full_data['company']}
Ticker: {full_data['ticker']}

Fake probability: {full_data['signals']['fake_data']['fake_probability']}
Fake label: {full_data['signals']['fake_data']['predicted_label']}
Sentiment label: {full_data['signals']['sentiment_data']['sentiment_label']}
Negative sentiment: {full_data['signals']['sentiment_data']['negative_score']}
Event type: {full_data['signals']['event']['event']}
Event score: {full_data['signals']['event']['event_score']}
Stance: {full_data['signals']['stance']['stance']}
Stance risk: {full_data['signals']['stance']['stance_risk']}
Alpha sentiment: {full_data['signals']['alpha_sentiment']}
Source trust: {full_data['signals']['source_trust']}
Rumor score: {full_data['rumor_score']}
Scam score: {full_data['signals']['scam_score']}

Price change percent: {full_data['market'].get('price_change_percent', 0.0)}
Market impact: {full_data['market'].get('market_impact_score', 0.0)}
Volatility: {full_data['market'].get('volatility', 0.0)}
Volume spike: {full_data['market'].get('volume_spike', 0.0)}

Final risk score: {full_data['risk_score']}
Final risk level: {full_data['risk_level']}

Important:
- Use EXACT risk level given
- Mention scam indicators if present
- Mention market movement
- Mention sentiment vs fake probability difference

Return JSON only.
"""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        return result["message"]["content"]

    except Exception as e:
        return f"""
{{
  "risk_level": "{full_data['risk_level']}",
  "summary": "LLM fallback used.",
  "reasoning": "Rule-based engine worked but LLM timed out.",
  "alert_message": "Ollama error: {str(e)}"
}}
"""