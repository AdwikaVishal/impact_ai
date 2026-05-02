"""
Strategic Analyzer Module
Identifies risks, tensions, and blind spots
"""
import requests
import os
from typing import List
from groq import Groq
from .models import Watchout


class StrategicAnalyzer:
    """Analyze strategic risks and opportunities"""
    
    def __init__(self):
        self.gnews_key = os.getenv("GNEWS_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None
    
    def analyze_watchouts(self, company_name: str, category: str) -> List[Watchout]:
        """
        Identify strategic watchouts before engaging the brand
        """
        # Get recent news for context
        news = self._get_recent_news(company_name)
        
        # Analyze with LLM
        watchouts = self._identify_watchouts(company_name, category, news)
        
        return watchouts
    
    def _get_recent_news(self, company_name: str) -> str:
        """Get recent news for context"""
        if not self.gnews_key:
            return ""
        
        try:
            response = requests.get(
                "https://gnews.io/api/v4/search",
                params={
                    "q": company_name,
                    "token": self.gnews_key,
                    "lang": "en",
                    "max": 5
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                # Combine headlines
                headlines = [article.get("title", "") for article in articles]
                return "\n".join(headlines)
            
        except Exception as e:
            print(f"Error fetching news: {e}")
        
        return ""
    
    def _identify_watchouts(self, company_name: str, category: str, news: str) -> List[Watchout]:
        """Identify strategic watchouts using LLM"""
        if not self.groq_client:
            return [
                Watchout(
                    risk_type="market_sentiment",
                    description="General market conditions should be monitored.",
                    severity="low"
                )
            ]
        
        try:
            prompt = f"""Analyze potential risks and watchouts before engaging {company_name} in the {category} industry.

Recent news context:
{news[:500] if news else "Limited recent news available"}

Identify 2-3 key watchouts in these categories:
1. Market sentiment risks (negative PR, controversies)
2. Reputational risks (scandals, legal issues)
3. Operational risks (layoffs, restructuring, financial troubles)

For each watchout, provide:
- Risk type
- Brief description (1 sentence)
- Severity (low, medium, high)

Format as:
RISK_TYPE | DESCRIPTION | SEVERITY

If no significant risks, return:
market_sentiment | No significant risks detected | low"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse watchouts
            watchouts = []
            for line in content.split("\n"):
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 3:
                        risk_type, description, severity = parts
                        watchouts.append(Watchout(
                            risk_type=risk_type.lower().replace(" ", "_"),
                            description=description,
                            severity=severity.lower()
                        ))
            
            return watchouts if watchouts else [
                Watchout(
                    risk_type="market_sentiment",
                    description="No significant risks detected in recent coverage.",
                    severity="low"
                )
            ]
            
        except Exception as e:
            print(f"Error identifying watchouts: {e}")
            return [
                Watchout(
                    risk_type="analysis_error",
                    description="Unable to complete risk analysis.",
                    severity="low"
                )
            ]
