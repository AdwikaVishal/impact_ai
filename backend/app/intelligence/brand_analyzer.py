"""
Brand Analyzer Module
Analyzes brand perception and market shifts
"""
import requests
import os
from typing import List, Dict
from datetime import datetime, timedelta
from groq import Groq


class BrandAnalyzer:
    """Analyze brand perception and market positioning"""
    
    def __init__(self):
        self.gnews_key = os.getenv("GNEWS_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None
    
    def analyze_brand(self, company_name: str) -> Dict:
        """
        Analyze brand perception and recent shifts
        """
        # Get recent news
        news_articles = self._get_recent_news(company_name)
        
        # Analyze perception
        perception = self._analyze_perception(company_name, news_articles)
        
        # Detect shifts
        shifts = self._detect_shifts(company_name, news_articles)
        
        return {
            "brand_perception": perception,
            "recent_shifts": shifts
        }
    
    def _get_recent_news(self, company_name: str, days: int = 90) -> List[Dict]:
        """Get recent news articles about the company"""
        if not self.gnews_key:
            return []
        
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            response = requests.get(
                "https://gnews.io/api/v4/search",
                params={
                    "q": company_name,
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
                return data.get("articles", [])
            
        except Exception as e:
            print(f"Error fetching news: {e}")
        
        return []
    
    def _analyze_perception(self, company_name: str, articles: List[Dict]) -> str:
        """Analyze brand perception from news articles"""
        if not self.groq_client or not articles:
            return f"Public perception of {company_name} appears neutral based on available information."
        
        try:
            # Prepare article summaries
            article_text = "\n".join([
                f"- {article.get('title', '')}: {article.get('description', '')[:100]}"
                for article in articles[:5]
            ])
            
            prompt = f"""Analyze the brand perception of {company_name} based on recent news coverage.

Recent headlines and descriptions:
{article_text}

Provide a 2-3 sentence analysis of:
1. Overall sentiment (positive, neutral, negative)
2. Key themes in coverage
3. Public perception trends

Be objective and factual."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error analyzing perception: {e}")
            return f"Brand perception analysis unavailable for {company_name}."
    
    def _detect_shifts(self, company_name: str, articles: List[Dict]) -> List[str]:
        """Detect recent market shifts or changes"""
        if not self.groq_client or not articles:
            return ["No significant market shifts detected in recent coverage."]
        
        try:
            # Prepare article summaries
            article_text = "\n".join([
                f"- {article.get('title', '')}"
                for article in articles[:10]
            ])
            
            prompt = f"""Identify any significant market shifts, pivots, or changes for {company_name} based on recent headlines.

Headlines:
{article_text}

List 2-3 key shifts or changes (if any). Examples:
- New product launches
- Strategic pivots
- Leadership changes
- Market expansion
- Rebranding efforts

If no significant shifts, return: "No major shifts detected."

Format as bullet points."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=250
            )
            
            # Parse bullet points
            content = response.choices[0].message.content.strip()
            shifts = [line.strip("- ").strip() for line in content.split("\n") if line.strip().startswith("-")]
            
            return shifts if shifts else [content]
            
        except Exception as e:
            print(f"Error detecting shifts: {e}")
            return ["Market shift analysis unavailable."]
