import os
import requests


API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")


def get_alpha_news_sentiment(company: str) -> float:
    if not API_KEY:
        return 0.0

    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "NEWS_SENTIMENT",
            "keywords": company,
            "apikey": API_KEY
        }

        res = requests.get(url, params=params, timeout=20)
        data = res.json()

        feed = data.get("feed", [])
        if not feed:
            return 0.0

        sentiments = []
        for item in feed[:5]:
            try:
                sentiments.append(float(item.get("overall_sentiment_score", 0)))
            except Exception:
                continue

        if not sentiments:
            return 0.0

        avg = sum(sentiments) / len(sentiments)
        return round(avg, 4)

    except Exception:
        return 0.0