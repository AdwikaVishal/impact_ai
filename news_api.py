import requests

NEWS_API_KEY = "YOUR_NEWS_KEY"

def get_live_news(query):
    try:
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
        res = requests.get(url).json()

        articles = res.get("articles", [])[:5]

        return [
            {
                "title": a["title"],
                "source": a["source"]["name"]
            }
            for a in articles
        ]
    except:
        return []