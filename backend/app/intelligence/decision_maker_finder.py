"""
Decision Maker Finder Module
Identifies key stakeholders using Hunter.io and web scraping
"""
import requests
import os
from typing import List, Dict
from .models import DecisionMaker


class DecisionMakerFinder:
    """Find and identify decision makers at target companies"""
    
    def __init__(self):
        self.hunter_key = os.getenv("HUNTER_API_KEY")
        self.prospeo_key = os.getenv("PROSPEO_API_KEY")
    
    def find_decision_makers(self, company_name: str, domain: str, category: str) -> List[DecisionMaker]:
        """
        Find decision makers using Prospeo API (primary) or Hunter.io (fallback)
        """
        # Try Prospeo first (better coverage)
        if self.prospeo_key:
            decision_makers = self._find_via_prospeo(company_name, domain, category)
            if decision_makers:
                print(f"✅ Found {len(decision_makers)} decision makers via Prospeo")
                return decision_makers
        
        # Fallback to Hunter.io
        if self.hunter_key:
            decision_makers = self._find_via_hunter(company_name, domain, category)
            if decision_makers:
                print(f"✅ Found {len(decision_makers)} decision makers via Hunter.io")
                return decision_makers
        
        # Last resort: fallback data
        print("⚠️  Using fallback decision makers")
        return self._fallback_decision_makers(company_name, category)
        
        try:
            # Get domain search results from Hunter.io
            response = requests.get(
                "https://api.hunter.io/v2/domain-search",
                params={
                    "domain": domain,
                    "api_key": self.hunter_key,
                    "limit": 10
                },
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"Hunter.io API error: {response.status_code}")
                return self._fallback_decision_makers(company_name, category)
            
            data = response.json()
            
            if not data.get("data"):
                return self._fallback_decision_makers(company_name, category)
            
            # Filter for relevant roles
            relevant_titles = [
                "cmo", "chief marketing", "vp marketing", "head of marketing",
                "brand manager", "marketing director", "ceo", "chief executive",
                "founder", "co-founder", "president", "director of communications"
            ]
            
            decision_makers = []
            
            for person in data["data"].get("emails", []):
                title = person.get("position", "").lower()
                
                # Check if title matches relevant roles
                if any(role in title for role in relevant_titles):
                    # Calculate relevance score
                    relevance = self._calculate_relevance(person.get("position", ""), category)
                    
                    decision_makers.append(DecisionMaker(
                        name=f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                        title=person.get("position", "Unknown"),
                        email=person.get("value"),  # email address
                        phone=person.get("phone_number"),
                        linkedin_url=person.get("linkedin"),
                        relevance_score=relevance
                    ))
            
            # Sort by relevance
            decision_makers.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return decision_makers[:5]  # Top 5
            
        except Exception as e:
            print(f"Error finding decision makers: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_decision_makers(company_name, category)
    
    def verify_email(self, email: str) -> Dict[str, any]:
        """
        Verify email address using Hunter.io
        """
        if not self.hunter_key:
            return {"valid": False, "confidence": 0}
        
        try:
            response = requests.get(
                "https://api.hunter.io/v2/email-verifier",
                params={
                    "email": email,
                    "api_key": self.hunter_key
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("data", {})
                
                return {
                    "valid": result.get("status") in ["valid", "accept_all"],
                    "confidence": result.get("score", 0),
                    "status": result.get("status"),
                    "smtp_check": result.get("smtp_check")
                }
        except Exception as e:
            print(f"Error verifying email: {e}")
        
        return {"valid": False, "confidence": 0}
    
    def _calculate_relevance(self, title: str, category: str) -> float:
        """
        Calculate relevance score based on title and category
        """
        title_lower = title.lower()
        
        # High relevance roles
        if any(role in title_lower for role in ["cmo", "chief marketing", "vp marketing"]):
            return 0.95
        
        # Medium-high relevance
        if any(role in title_lower for role in ["head of marketing", "marketing director", "brand manager"]):
            return 0.85
        
        # Medium relevance
        if any(role in title_lower for role in ["ceo", "founder", "president"]):
            return 0.75
        
        # Lower relevance
        if "marketing" in title_lower or "brand" in title_lower:
            return 0.65
        
        return 0.5
    
    def _fallback_decision_makers(self, company_name: str, category: str) -> List[DecisionMaker]:
        """
        Fallback decision makers when API fails
        """
        # Generic roles based on company size/category
        return [
            DecisionMaker(
                name="Marketing Head",
                title="Chief Marketing Officer",
                email=None,
                phone=None,
                linkedin_url=None,
                relevance_score=0.95
            ),
            DecisionMaker(
                name="Brand Manager",
                title="Senior Brand Manager",
                email=None,
                phone=None,
                linkedin_url=None,
                relevance_score=0.85
            ),
            DecisionMaker(
                name="Communications Director",
                title="Director of Communications",
                email=None,
                phone=None,
                linkedin_url=None,
                relevance_score=0.80
            )
        ]
    
    def enrich_with_linkedin(self, decision_makers: List[DecisionMaker], company_name: str) -> List[DecisionMaker]:
        """
        Enrich decision makers with LinkedIn profiles
        Note: This is a placeholder - actual LinkedIn scraping requires authentication
        """
        for dm in decision_makers:
            if not dm.linkedin_url:
                # Construct likely LinkedIn URL
                name_parts = dm.name.lower().split()
                if len(name_parts) >= 2:
                    linkedin_slug = f"{name_parts[0]}-{name_parts[-1]}"
                    dm.linkedin_url = f"https://www.linkedin.com/in/{linkedin_slug}"
        
        return decision_makers
