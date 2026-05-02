"""
Company Profiler Module
Analyzes business model, positioning, and scale metrics
"""
import requests
import os
from typing import Dict, List
from groq import Groq


class CompanyProfiler:
    """Profile companies using web search and LLM analysis"""
    
    def __init__(self):
        self.serper_key = os.getenv("SERPER_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None
    
    def profile_company(self, company_name: str, category: str) -> Dict:
        """
        Generate comprehensive company profile
        """
        # Gather information from web
        company_info = self._search_company_info(company_name)
        
        # Analyze with LLM
        business_model = self._analyze_business_model(company_name, category, company_info)
        positioning = self._analyze_positioning(company_name, category, company_info)
        scale_metrics = self._estimate_scale(company_name, company_info)
        
        return {
            "business_model": business_model,
            "positioning": positioning,
            "scale_metrics": scale_metrics
        }
    
    def _search_company_info(self, company_name: str) -> str:
        """Search for company information using Serper API"""
        if not self.serper_key:
            return f"Limited information available for {company_name}"
        
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": self.serper_key,
                    "Content-Type": "application/json"
                },
                json={
                    "q": f"{company_name} company overview business model",
                    "num": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                
                # Extract snippets
                snippets = []
                for item in results.get("organic", [])[:5]:
                    snippet = item.get("snippet", "")
                    if snippet:
                        snippets.append(snippet)
                
                return " ".join(snippets)
            
        except Exception as e:
            print(f"Error searching company info: {e}")
        
        return f"Limited information available for {company_name}"
    
    def _analyze_business_model(self, company_name: str, category: str, info: str) -> str:
        """Analyze business model using LLM"""
        if not self.groq_client:
            return f"{company_name} operates in the {category} industry with a standard business model."
        
        try:
            prompt = f"""Analyze the business model of {company_name} in the {category} industry.

Context: {info[:1000]}

Provide a concise 2-3 sentence analysis covering:
1. Revenue model (B2B, B2C, subscription, marketplace, etc.)
2. Value proposition
3. Key business activities

Keep it factual and professional."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error analyzing business model: {e}")
            return f"{company_name} operates in the {category} industry."
    
    def _analyze_positioning(self, company_name: str, category: str, info: str) -> str:
        """Analyze market positioning using LLM"""
        if not self.groq_client:
            return f"{company_name} is positioned as a key player in the {category} market."
        
        try:
            prompt = f"""Analyze the market positioning of {company_name} in the {category} industry.

Context: {info[:1000]}

Provide a concise 2-3 sentence analysis covering:
1. Target market segment
2. Unique selling proposition
3. Competitive differentiation

Keep it factual and professional."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error analyzing positioning: {e}")
            return f"{company_name} is positioned in the {category} market."
    
    def _estimate_scale(self, company_name: str, info: str) -> Dict:
        """Estimate company scale metrics"""
        # Extract metrics from search results
        metrics = {
            "size": "Unknown",
            "employees": "Unknown",
            "revenue": "Unknown",
            "market_presence": "Regional"
        }
        
        # Simple keyword-based extraction
        info_lower = info.lower()
        
        # Size estimation
        if any(word in info_lower for word in ["fortune 500", "global leader", "multinational"]):
            metrics["size"] = "Enterprise"
            metrics["market_presence"] = "Global"
        elif any(word in info_lower for word in ["startup", "founded 20", "series"]):
            metrics["size"] = "Startup"
        elif any(word in info_lower for word in ["mid-size", "growing", "regional"]):
            metrics["size"] = "Mid-Market"
        
        # Employee estimation
        if "employees" in info_lower or "staff" in info_lower:
            # Try to extract number
            import re
            numbers = re.findall(r'(\d+(?:,\d+)*)\s*(?:employees|staff)', info_lower)
            if numbers:
                metrics["employees"] = numbers[0]
        
        return metrics
