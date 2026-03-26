import yfinance as yf

FALLBACK_TICKERS = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy Services": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "State Bank of India": "SBIN.NS",
    "Wipro": "WIPRO.NS",
    "Axis Bank": "AXISBANK.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Jubilant FoodWorks": "JUBLFOOD.NS",
    "Tesla Inc.": "TSLA",
    "Apple Inc.": "AAPL",
    "Amazon": "AMZN",
    "Alphabet Inc.": "GOOGL",
    "Meta": "META"
}


def _validate_ticker(symbol: str) -> bool:
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="5d")
        return not hist.empty
    except Exception:
        return False


def resolve_ticker(company_name: str):
    if not company_name or company_name == "Unknown":
        return None

    if company_name in FALLBACK_TICKERS:
        return FALLBACK_TICKERS[company_name]

    possible = [
        company_name.replace(" ", "") + ".NS",
        company_name.replace(" ", "") + ".BO",
        company_name.upper().replace(" ", "")
    ]

    for symbol in possible:
        if _validate_ticker(symbol):
            return symbol

    return None