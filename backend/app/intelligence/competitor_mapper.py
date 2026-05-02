"""
Competitor Mapping Module
Discovers and analyzes competitors using web search and APIs
"""
import requests
import os
from typing import List, Dict
from .models import Competitor


class CompetitorMapper:
    """Discover and analyze competitors"""
    
    def __init__(self):
        self.serper_key = os.getenv("SERPER_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
    
    def discover_competitors(self, company_name: str, category: str, max_results: int = 5) -> List[Competitor]:
        """
        Discover competitors using Serper API (Google Search)
        """
        if not self.serper_key:
            print("⚠️  SERPER_KEY not found, using fallback")
            return self._fallback_competitors(company_name, category)
        
        try:
            # Search for competitors
            search_query = f"{company_name} competitors {category}"
            
            response = requests.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": self.serper_key,
                    "Content-Type": "application/json"
                },
                json={
                    "q": search_query,
                    "num": 10
                },
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"Serper API error: {response.status_code}")
                return self._fallback_competitors(company_name, category)
            
            results = response.json()
            
            # Extract competitor names from search results
            competitors = []
            seen_domains = set()
            
            for item in results.get("organic", [])[:max_results]:
                domain = self._extract_domain(item.get("link", ""))
                if domain and domain not in seen_domains:
                    seen_domains.add(domain)
                    
                    competitors.append(Competitor(
                        name=self._extract_company_name(item.get("title", "")),
                        domain=domain,
                        relevance_score=0.8,  # Base score
                        strengths=["Market presence"],
                        weaknesses=[]
                    ))
            
            return competitors[:max_results]
            
        except Exception as e:
            print(f"Error discovering competitors: {e}")
            return self._fallback_competitors(company_name, category)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            return domain
        except:
            return ""
    
    def _extract_company_name(self, title: str) -> str:
        """Extract company name from search result title"""
        # Remove common suffixes
        for suffix in [" - Official Site", " | ", " - ", "..."]:
            if suffix in title:
                title = title.split(suffix)[0]
        return title.strip()
    
    def _fallback_competitors(self, company_name: str, category: str) -> List[Competitor]:
        """Fallback competitor list when API fails"""
        # Industry-specific fallbacks
        fallback_map = {
            "automotive": [
                Competitor(name="Tesla", domain="tesla.com", relevance_score=0.9, strengths=["Innovation", "Brand"], weaknesses=[]),
                Competitor(name="Ford", domain="ford.com", relevance_score=0.85, strengths=["Legacy", "Scale"], weaknesses=[]),
                Competitor(name="GM", domain="gm.com", relevance_score=0.85, strengths=["Manufacturing"], weaknesses=[]),
            ],
            "tech": [
                Competitor(name="Microsoft", domain="microsoft.com", relevance_score=0.9, strengths=["Enterprise"], weaknesses=[]),
                Competitor(name="Google", domain="google.com", relevance_score=0.9, strengths=["AI", "Cloud"], weaknesses=[]),
                Competitor(name="Amazon", domain="amazon.com", relevance_score=0.85, strengths=["Cloud", "Scale"], weaknesses=[]),
            ],
            "ecommerce": [
                Competitor(name="Amazon", domain="amazon.com", relevance_score=0.95, strengths=["Scale", "Logistics"], weaknesses=[]),
                Competitor(name="Shopify", domain="shopify.com", relevance_score=0.85, strengths=["Platform"], weaknesses=[]),
                Competitor(name="eBay", domain="ebay.com", relevance_score=0.8, strengths=["Marketplace"], weaknesses=[]),
            ]
        }
        
        # Try to match category
        category_lower = category.lower()
        for key, competitors in fallback_map.items():
            if key in category_lower:
                return competitors[:3]
        
        # Generic fallback
        return [
            Competitor(
                name=f"Competitor 1 in {category}",
                domain="example1.com",
                relevance_score=0.7,
                strengths=["Market presence"],
                weaknesses=[]
            ),
            Competitor(
                name=f"Competitor 2 in {category}",
                domain="example2.com",
                relevance_score=0.65,
                strengths=["Innovation"],
                weaknesses=[]
            ),
            Competitor(
                name=f"Competitor 3 in {category}",
                domain="example3.com",
                relevance_score=0.6,
                strengths=["Customer base"],
                weaknesses=[]
            )
        ]
    
    def analyze_competitor_strengths(self, competitors: List[Competitor]) -> List[Competitor]:
        """
        Analyze competitor strengths using LLM
        """
        if not self.groq_key:
            return competitors
        
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_key)
            
            for competitor in competitors:
                prompt = f"""Analyze this competitor and list 3 key strengths and 2 potential weaknesses:
                
Company: {competitor.name}
Domain: {competitor.domain}

Provide a brief analysis in this format:
STRENGTHS:
1. [strength]
2. [strength]
3. [strength]

WEAKNESSES:
1. [weakness]
2. [weakness]
"""
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=300
                )
                
                analysis = response.choices[0].message.content
                
                # Parse strengths and weaknesses
                strengths = []
                weaknesses = []
                
                lines = analysis.split("\n")
                current_section = None
                
                for line in lines:
                    line = line.strip()
                    if "STRENGTHS:" in line:
                        current_section = "strengths"
                    elif "WEAKNESSES:" in line:
                        current_section = "weaknesses"
                    elif line and line[0].isdigit():
                        # Extract bullet point
                        text = line.split(".", 1)[1].strip() if "." in line else line
                        if current_section == "strengths":
                            strengths.append(text)
                        elif current_section == "weaknesses":
                            weaknesses.append(text)
                
                competitor.strengths = strengths[:3]
                competitor.weaknesses = weaknesses[:2]
            
            return competitors
            
        except Exception as e:
            print(f"Error analyzing competitors: {e}")
            return competitors
