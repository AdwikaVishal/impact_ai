"""
LLM Client for Groq API Integration
Provides AI-powered headline analysis and explanations using Groq's fast inference
"""

import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class GroqClient:
    """Client for Groq API - Fast LLM Inference"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"  # Groq API endpoint
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # Default model
        
        if not self.api_key:
            print("Warning: GROQ_API_KEY not found in environment variables")
    
    def analyze_headline(self, headline: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a financial headline using Groq AI
        
        Args:
            headline: The headline text to analyze
            
        Returns:
            Dictionary with AI analysis or None if error
        """
        if not self.api_key:
            return None
        
        prompt = f"""Analyze this financial headline and provide:
1. Sentiment (positive/negative/neutral) with confidence score
2. Key entities (companies, people, events)
3. Potential market impact
4. Risk assessment
5. Trading recommendation

Headline: "{headline}"

Respond in JSON format."""

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a financial analyst AI specializing in market news analysis."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,  # Lower temperature for more consistent analysis
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "analysis": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "model": self.model
                }
            else:
                print(f"Groq API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return None
    
    def generate_explanation(self, analysis_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a natural language explanation of the analysis
        
        Args:
            analysis_data: Dictionary containing analysis results
            
        Returns:
            Natural language explanation or None if error
        """
        if not self.api_key:
            return None
        
        prompt = f"""Based on this headline analysis, provide a clear, concise explanation for investors:

Risk Score: {analysis_data.get('risk_score')}
Trading Signal: {analysis_data.get('trading_signal')}
Sentiment: {analysis_data.get('analysis', {}).get('sentiment', {}).get('label')}
Fake News Probability: {analysis_data.get('analysis', {}).get('fake_news_detection', {}).get('fake_probability')}

Explain in 2-3 sentences what this means for investors."""

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a financial advisor explaining market analysis to retail investors."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.5,
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                return None
                
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return None


# Singleton instance
_groq_client = None

def get_groq_client() -> GroqClient:
    """Get or create Groq client instance"""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client
