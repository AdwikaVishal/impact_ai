import json
import streamlit as st

from models import fake_news_clf, sentiment_clf, ner_clf, event_clf, stance_clf
from brain import (
    extract_company,
    compute_brain_signals,
    calculate_final_score,
    ask_llm_brain
)
from entity_resolver import normalize_entity
from market_data import get_market_data
from source_checker import get_source_trust
from rumor_detector import get_rumor_score
from ai_signal import get_ai_signal
from prediction import get_prediction
from news_api import get_live_news

st.set_page_config(page_title="MarketShield AI", layout="wide")

st.title("🚀 MarketShield AI")
st.subheader("Global Financial Misinformation Risk Analyzer")


def get_tradingview_symbol(ticker: str) -> str:
    """
    Convert ticker into TradingView-compatible format.
    """
    if not ticker or ticker in ["Unknown", "Not Found", "Not Listed"]:
        return ""

    ticker = ticker.strip().upper()

    # Reject invalid symbols
    if ticker.startswith("^") or "-" in ticker:
        return ""

    # Indian NSE
    if ticker.endswith(".NS"):
        return f"NSE:{ticker.replace('.NS', '')}"

    # Indian BSE
    if ticker.endswith(".BO"):
        return f"BSE:{ticker.replace('.BO', '')}"

    # US stocks default
    if "." not in ticker:
        return f"NASDAQ:{ticker}"

    return ""


headline = st.text_area(
    "Enter a financial headline",
    placeholder="Example: Tesla stock drops after weak delivery numbers and speculation about demand."
)

if st.button("Analyze"):
    if not headline.strip():
        st.warning("Please enter a headline.")
    else:
        with st.spinner("Analyzing..."):
            # 1. Entity extraction
            entities = ner_clf(headline[:500])
            raw_company = extract_company(entities)

            # 2. Normalize abbreviations
            entity_data = normalize_entity(raw_company)
            display_name = entity_data["display_name"]
            market_entity = entity_data["market_entity"]

            # 3. Global resolution + market data
            market = get_market_data(market_entity)

            # 4. Use resolved name if available
            final_company_name = market.get("resolved_name", display_name) or display_name

            # 5. Other signals
            source_trust = get_source_trust(headline)
            rumor_score = get_rumor_score(headline)

            models = {
                "fake": fake_news_clf,
                "sentiment": sentiment_clf,
                "event": event_clf,
                "stance": stance_clf
            }

            # 6. Brain signals
            signals = compute_brain_signals(
                headline=headline,
                models=models,
                market_data=market,
                source_trust=source_trust
            )

            # 7. Final risk
            risk_score, risk_level = calculate_final_score(
                signals=signals,
                market=market,
                rumor_score=rumor_score
            )

            # 8. Extra modules
            prediction = None
            try:
                prediction = get_prediction(market["ticker"])
            except Exception:
                prediction = None

            ai_signal = get_ai_signal(
                market.get("price_change_percent", 0.0),
                market.get("volume_spike", 0.0),
                signals["sentiment_data"]["sentiment_score"]
            )

            live_news = get_live_news(final_company_name)

            # 9. Final payload
            final_payload = {
                "headline": headline,
                "company": final_company_name,
                "ticker": market["ticker"],
                "market": market,
                "signals": signals,
                "rumor_score": rumor_score,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "prediction": prediction,
                "ai_signal": ai_signal
            }

            # 10. LLM output
            llm_output = ask_llm_brain(final_payload)

            try:
                llm_json = json.loads(llm_output)
            except Exception:
                llm_json = {
                    "risk_level": risk_level,
                    "summary": llm_output,
                    "reasoning": llm_output,
                    "alert_message": llm_output
                }

        # =========================
        # RISK BANNER
        # =========================
        if risk_level == "High":
            st.error(f"⚠️ Risk Level: {risk_level}")
        elif risk_level == "Medium":
            st.warning(f"⚠️ Risk Level: {risk_level}")
        else:
            st.success(f"✅ Risk Level: {risk_level}")

        # =========================
        # TOP METRICS
        # =========================
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Resolved Company", final_company_name)
        c2.metric("Ticker", market.get("ticker", "N/A"))
        c3.metric("Risk Score", risk_score)
        c4.metric("AI Signal", ai_signal)

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Fake Probability", signals["fake_data"]["fake_probability"])
        c6.metric("Sentiment", signals["sentiment_data"]["sentiment_label"])
        c7.metric("Event", signals["event"]["event"])
        c8.metric("Stance", signals["stance"]["stance"])

        c9, c10, c11, c12 = st.columns(4)
        c9.metric("Price Change %", market.get("price_change_percent", 0.0))
        c10.metric("Volatility", market.get("volatility", 0.0))
        c11.metric("Volume Spike", market.get("volume_spike", 0.0))
        c12.metric("Source Trust", signals["source_trust"])

        # =========================
        # RESOLUTION INFO
        # =========================
        st.subheader("Resolver Details")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Raw Entity", raw_company)
        r2.metric("Exchange", market.get("exchange", "") or "N/A")
        r3.metric("Resolver Source", market.get("resolver_source", "") or "N/A")
        r4.metric("Resolver Status", market.get("resolver_status", "") or "N/A")

        # =========================
        # MARKET DATA
        # =========================
        st.subheader("Market Data")
        st.json(market)

        # =========================
        # PREDICTION
        # =========================
        st.subheader("Prediction")
        if prediction:
            p1, p2 = st.columns(2)
            p1.metric("Expected Price", prediction.get("expected_price", "N/A"))
            p2.metric("Predicted Volatility", prediction.get("volatility", "N/A"))
        else:
            st.info("Prediction not available for this entity.")

        # =========================
        # LIVE NEWS
        # =========================
        st.subheader("Live News")
        if live_news:
            for item in live_news:
                st.write(f"• {item['title']} ({item['source']})")
        else:
            st.info("No live news found.")

        # =========================
        # STOCK CHART
        # =========================
        st.subheader("Stock Chart")
        tv_symbol = get_tradingview_symbol(market.get("ticker", ""))

        if tv_symbol:
            st.components.v1.html(
                f"""
                <script src="https://s3.tradingview.com/tv.js"></script>
                <div id="chart"></div>
                <script>
                new TradingView.widget({{
                    "container_id": "chart",
                    "width": "100%",
                    "height": 500,
                    "symbol": "{tv_symbol}",
                    "interval": "D",
                    "timezone": "Asia/Kolkata",
                    "theme": "dark",
                    "style": "1",
                    "locale": "en",
                    "toolbar_bg": "#0f172a",
                    "enable_publishing": false,
                    "allow_symbol_change": true
                }});
                </script>
                """,
                height=520
            )
        else:
            st.warning("⚠️ Chart not available for this entity or ticker format is unsupported.")

        # =========================
        # AI EXPLANATION
        # =========================
        st.subheader("AI Explanation")
        st.write(f"**Summary:** {llm_json.get('summary', '')}")
        st.write(f"**Reasoning:** {llm_json.get('reasoning', '')}")
        st.write(f"**Alert Message:** {llm_json.get('alert_message', '')}")

        # =========================
        # DEBUG
        # =========================
        with st.expander("Structured Brain Payload"):
            st.json(final_payload)

        with st.expander("Signals"):
            st.json(signals)

        with st.expander("Raw LLM Output"):
            st.code(llm_output, language="json")