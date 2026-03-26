def get_ai_signal(price_change, volume_spike, sentiment_score):
    if price_change > 0 and volume_spike > 1.5 and sentiment_score > 0.6:
        return "🟢 Bullish"
    elif price_change < 0 and sentiment_score < 0.4:
        return "🔴 Bearish"
    else:
        return "🟡 Neutral"