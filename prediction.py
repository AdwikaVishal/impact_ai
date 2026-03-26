import requests

API_KEY = "YOUR_ALPHA_KEY"

def get_prediction(symbol):
    if symbol in ["Not Listed", "Not Found"]:
        return None

    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
        res = requests.get(url).json()

        series = res.get("Time Series (Daily)", {})
        if not series:
            return None

        prices = [float(v["4. close"]) for v in list(series.values())[:30]][::-1]

        returns = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]

        avg = sum(returns) / len(returns)
        volatility = (sum((r - avg) ** 2 for r in returns) / len(returns)) ** 0.5

        last_price = prices[-1]
        expected = last_price * (1 + avg * 10)

        return {
            "expected_price": round(expected, 2),
            "volatility": round(volatility, 4)
        }

    except:
        return None