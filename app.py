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

st.set_page_config(page_title="MarketShield AI", layout="wide")

st.title("MarketShield AI")
st.subheader("Financial Misinformation Risk Analyzer")

headline = st.text_area(
    "Enter a financial headline",
    placeholder="Example: Reliance shares plunge after fraud rumors spread online from unknown sources."
)

if st.button("Analyze"):
    if not headline.strip():
        st.warning("Please enter a headline.")
    else:
        with st.spinner("Analyzing..."):
            entities = ner_clf(headline[:500])
            raw_company = extract_company(entities)

            entity_data = normalize_entity(raw_company)
            display_name = entity_data["display_name"]
            market_entity = entity_data["market_entity"]

            market = get_market_data(market_entity)
            source_trust = get_source_trust(headline)
            rumor_score = get_rumor_score(headline)

            models = {
                "fake": fake_news_clf,
                "sentiment": sentiment_clf,
                "event": event_clf,
                "stance": stance_clf
            }

            signals = compute_brain_signals(
                headline=headline,
                models=models,
                market_data=market,
                source_trust=source_trust
            )

            risk_score, risk_level = calculate_final_score(
                signals=signals,
                market=market,
                rumor_score=rumor_score
            )

            final_payload = {
                "headline": headline,
                "company": display_name,
                "ticker": market["ticker"],
                "market": market,
                "signals": signals,
                "rumor_score": rumor_score,
                "risk_score": risk_score,
                "risk_level": risk_level
            }

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

        if risk_level == "High":
            st.error(f"Risk Level: {risk_level}")
        elif risk_level == "Medium":
            st.warning(f"Risk Level: {risk_level}")
        else:
            st.success(f"Risk Level: {risk_level}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Company", display_name)
        c2.metric("Ticker", market["ticker"])
        c3.metric("Risk Score", risk_score)
        c4.metric("Rumor Score", rumor_score)

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Fake Probability", signals["fake_data"]["fake_probability"])
        c6.metric("Sentiment", signals["sentiment_data"]["sentiment_label"])
        c7.metric("Event", signals["event"]["event"])
        c8.metric("Stance", signals["stance"]["stance"])

        c9, c10, c11, c12 = st.columns(4)
        c9.metric("Price Change %", market["price_change_percent"])
        c10.metric("Volatility", market["volatility"])
        c11.metric("Volume Spike", market["volume_spike"])
        c12.metric("Source Trust", signals["source_trust"])

        st.divider()
        st.subheader("LLM Explanation")
        st.write(f"**Summary:** {llm_json.get('summary', '')}")
        st.write(f"**Reasoning:** {llm_json.get('reasoning', '')}")
        st.write(f"**Alert Message:** {llm_json.get('alert_message', '')}")

        with st.expander("Structured Brain Payload"):
            st.json(final_payload)

        with st.expander("Raw LLM Output"):
            st.code(llm_output, language="json")