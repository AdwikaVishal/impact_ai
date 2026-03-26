from ....news_api import get_live_news  # Migrated root

def get_company_news(symbol):
    return get_live_news(symbol)

