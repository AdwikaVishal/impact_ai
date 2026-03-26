import os
import requests
import yfinance as yf
from yfinance import Search

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")


def _validate_ticker(symbol: str) -> bool:
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="5d")
        return not hist.empty
    except Exception:
        return False


def _search_yfinance(company_name: str):
    try:
        search = Search(query=company_name, max_results=8)
        quotes = getattr(search, "quotes", []) or []

        for q in quotes:
            symbol = q.get("symbol")
            shortname = q.get("shortname") or q.get("longname") or company_name
            exchange = q.get("exchange") or q.get("exchDisp") or ""
            quote_type = q.get("quoteType") or ""

            if symbol and quote_type in ["EQUITY", "ETF", "MUTUALFUND", "INDEX", ""]:
                return {
                    "ticker": symbol,
                    "resolved_name": shortname,
                    "exchange": exchange,
                    "source": "yfinance_search"
                }

        return None
    except Exception:
        return None


def _search_alpha_vantage(company_name: str):
    if not ALPHA_VANTAGE_API_KEY:
        return None

    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": company_name,
            "apikey": ALPHA_VANTAGE_API_KEY
        }

        res = requests.get(url, params=params, timeout=20)
        data = res.json()
        matches = data.get("bestMatches", [])

        if not matches:
            return None

        best = matches[0]

        symbol = best.get("1. symbol", "")
        name = best.get("2. name", company_name)
        region = best.get("4. region", "")
        match_score = best.get("9. matchScore", "")

        return {
            "ticker": symbol,
            "resolved_name": name,
            "exchange": region,
            "match_score": match_score,
            "source": "alpha_vantage_search"
        }
    except Exception:
        return None


def resolve_ticker(company_name: str) -> dict:
    """
    Returns:
    {
        "ticker": "...",
        "resolved_name": "...",
        "exchange": "...",
        "source": "...",
        "status": "ok" | "not_found"
    }
    """
    if not company_name or company_name == "Unknown":
        return {
            "ticker": "Not Found",
            "resolved_name": company_name or "Unknown",
            "exchange": "",
            "source": "none",
            "status": "not_found"
        }

    # 1. Try yfinance search first
    yf_result = _search_yfinance(company_name)
    if yf_result and yf_result.get("ticker"):
        return {
            **yf_result,
            "status": "ok"
        }

    # 2. Try Alpha Vantage official symbol search
    av_result = _search_alpha_vantage(company_name)
    if av_result and av_result.get("ticker"):
        return {
            **av_result,
            "status": "ok"
        }

    # 3. Try direct guessed symbols as last fallback
    guesses = [
        company_name.replace(" ", "") + ".NS",
        company_name.replace(" ", "") + ".BO",
        company_name.upper().replace(" ", "")
    ]

    for g in guesses:
        if _validate_ticker(g):
            return {
                "ticker": g,
                "resolved_name": company_name,
                "exchange": "",
                "source": "guessed_symbol",
                "status": "ok"
            }

    return {
        "ticker": "Not Found",
        "resolved_name": company_name,
        "exchange": "",
        "source": "none",
        "status": "not_found"
    }