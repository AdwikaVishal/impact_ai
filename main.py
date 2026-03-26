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


def main():
    headline = input("Enter headline: ").strip()

    if not headline:
        print("No headline entered.")
        return

    entities = ner_clf(headline[:500])
    raw_company = extract_company(entities)

    entity_data = normalize_entity(raw_company)
    display_name = entity_data["display_name"]
    market_entity = entity_data["market_entity"]

    market = get_market_data(market_entity)

    # If online resolver found a better company name, use it
    final_company_name = market.get("resolved_name", display_name) or display_name

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
        "company": final_company_name,
        "ticker": market["ticker"],
        "market": market,
        "signals": signals,
        "rumor_score": rumor_score,
        "risk_score": risk_score,
        "risk_level": risk_level
    }

    print("\nResolved raw entity:", raw_company)
    print("Final company name:", final_company_name)
    print("Ticker:", market["ticker"])
    print("Resolver source:", market.get("resolver_source"))
    print("Exchange:", market.get("exchange"))

    print("\nSignals:")
    print(signals)

    print("\nMarket:")
    print(market)

    print("\nRisk:", risk_level, risk_score)

    print("\nLLM Output:")
    print(ask_llm_brain(final_payload))


if __name__ == "__main__":
    main()