"""
Activity Tracker Module
Tracks brand activities, campaigns, and launches
"""
import requests
import os
from typing import List
from datetime import datetime, timedelta
from .models import BrandActivity


class ActivityTracker:
    """Track brand activities and campaigns"""
    
    def __init__(self):
        self.gnews_key = os.getenv("GNEWS_API_KEY")
        self.serper_key = os.getenv("SERPER_KEY")
    
    def track_activities(self, company_name: str, months: int = 12) -> List[BrandActivity]:
        """
        Track brand activities over the past N months
        """
        activities = []
        
        # Get news-based activities
        news_activities = self._track_from_news(company_name, months)
        activities.extend(news_activities)
        
        # Get search-based activities
        search_activities = self._track_from_search(company_name)
        activities.extend(search_activities)
        
        # Sort by date (most recent first)
        activities.sort(key=lambda x: x.date, reverse=True)
        
        return activities[:20]  # Return top 20
    
    def _track_from_news(self, company_name: str, months: int) -> List[BrandActivity]:
        """Track activities from news articles"""
        if not self.gnews_key:
            return []
        
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=months * 30)
            
            response = requests.get(
                "https://gnews.io/api/v4/search",
                params={
                    "q": f"{company_name} (launch OR campaign OR partnership OR announcement)",
                    "token": self.gnews_key,
                    "lang": "en",
                    "max": 10,
                    "from": from_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "to": to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                activities = []
                for article in articles:
                    # Determine activity type from title/description
                    title = article.get("title", "").lower()
                    activity_type = self._classify_activity(title)
                    
                    activities.append(BrandActivity(
                        title=article.get("title", ""),
                        description=article.get("description", "")[:200],
                        date=article.get("publishedAt", "")[:10],
                        activity_type=activity_type,
                        source_url=article.get("url", "")
                    ))
                
                return activities
            
        except Exception as e:
            print(f"Error tracking from news: {e}")
        
        return []
    
    def _track_from_search(self, company_name: str) -> List[BrandActivity]:
        """Track activities from web search"""
        if not self.serper_key:
            return []
        
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": self.serper_key,
                    "Content-Type": "application/json"
                },
                json={
                    "q": f"{company_name} recent campaigns launches 2026",
                    "num": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                
                activities = []
                for item in results.get("organic", [])[:5]:
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    
                    activities.append(BrandActivity(
                        title=title,
                        description=snippet[:200],
                        date=datetime.now().strftime("%Y-%m-%d"),
                        activity_type=self._classify_activity(title.lower()),
                        source_url=item.get("link", "")
                    ))
                
                return activities
            
        except Exception as e:
            print(f"Error tracking from search: {e}")
        
        return []
    
    def _classify_activity(self, text: str) -> str:
        """Classify activity type from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["launch", "launches", "unveils", "introduces"]):
            return "launch"
        elif any(word in text_lower for word in ["campaign", "marketing", "advertising"]):
            return "campaign"
        elif any(word in text_lower for word in ["partnership", "partners", "collaboration"]):
            return "partnership"
        elif any(word in text_lower for word in ["press release", "announces", "announcement"]):
            return "press"
        else:
            return "general"
