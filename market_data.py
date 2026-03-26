import yfinance as yf
from ticker_resolver import resolve_ticker

NON_LISTED = {
    "Reserve Bank of India",
    "Securities and Exchange Board of India",
    "Government of India",
    "Ministry of Finance"
}


def _empty_market_payload(ticker_value):
    return {
        "ticker": ticker_value,
        "price_change_percent": 0.0,
        "market_impact_score": 0.0,
        "volatility": 0.0,
        "volume_spike": 0.0
    }


def get_market_data(company_name: str) -> dict:
    if company_name in NON_LISTED:
        return _empty_market_payload("Not Listed")

    ticker = resolve_ticker(company_name)

    if not ticker:
        return _empty_market_payload("Not Found")

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")

        if hist.empty or len(hist) < 2:
            return _empty_market_payload(ticker)

        prices = hist["Close"].tolist()
        volumes = hist["Volume"].tolist()

        prev_close = prices[-2]
        latest_close = prices[-1]

        pct_change = ((latest_close - prev_close) / prev_close) * 100 if prev_close else 0.0

        changes = [
            abs((prices[i] - prices[i - 1]) / prices[i - 1])
            for i in range(1, len(prices))
            if prices[i - 1] != 0
        ]
        volatility = sum(changes) / len(changes) if changes else 0.0

        avg_volume = 0.0
        if len(volumes) > 1:
            base_volumes = volumes[:-1]
            avg_volume = sum(base_volumes) / len(base_volumes) if base_volumes else 0.0

        latest_volume = volumes[-1] if volumes else 0.0
        volume_spike = (latest_volume / avg_volume) if avg_volume else 1.0

        abs_move = abs(pct_change)

        if abs_move >= 3:
            impact_score = 1.0
        elif abs_move >= 1.5:
            impact_score = 0.7
        elif abs_move >= 0.5:
            impact_score = 0.4
        else:
            impact_score = 0.1

        return {
            "ticker": ticker,
            "price_change_percent": round(pct_change, 2),
            "market_impact_score": round(impact_score, 2),
            "volatility": round(volatility, 4),
            "volume_spike": round(volume_spike, 2)
        }

    except Exception:
        return _empty_market_payload(ticker)