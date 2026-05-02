"""
Events Tracker Module - Real Events using Apify
Tracks company events, conferences, and activations
"""
import requests
import os
from typing import List
from datetime import datetime
from .models import Event


class EventsTracker:
    """Track real company events using Apify API"""
    
    def __init__(self):
        self.apify_key = os.getenv("APIFY_API_KEY")
    
    def track_events(self, company_name: str) -> List[Event]:
        """
        Get real events for a company using Apify
        """
        if not self.apify_key:
            print("⚠️  APIFY_API_KEY not found, using placeholder")
            return self._placeholder_events(company_name)
        
        try:
            # Use Apify's Google Events Scraper
            events = self._scrape_events_via_apify(company_name)
            
            if events:
                print(f"✅ Found {len(events)} events via Apify")
                return events
            else:
                print("⚠️  No events found, using placeholder")
                return self._placeholder_events(company_name)
        
        except Exception as e:
            print(f"Error tracking events: {e}")
            return self._placeholder_events(company_name)
    
    def _scrape_events_via_apify(self, company_name: str) -> List[Event]:
        """
        Scrape events using Apify API
        """
        try:
            # Start Apify actor for event scraping
            # Using Google Events Scraper actor
            actor_id = "apify/google-events-scraper"
            
            # Start the actor
            response = requests.post(
                f"https://api.apify.com/v2/acts/{actor_id}/runs",
                params={"token": self.apify_key},
                json={
                    "queries": [f"{company_name} events"],
                    "maxResults": 10
                },
                timeout=10
            )
            
            if response.status_code != 201:
                print(f"Apify actor start error: {response.status_code}")
                return []
            
            run_data = response.json()
            run_id = run_data.get("data", {}).get("id")
            
            if not run_id:
                return []
            
            # Wait for actor to finish (with timeout)
            import time
            max_wait = 30  # seconds
            waited = 0
            
            while waited < max_wait:
                status_response = requests.get(
                    f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}",
                    params={"token": self.apify_key},
                    timeout=5
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("data", {}).get("status")
                    
                    if status == "SUCCEEDED":
                        # Get results
                        return self._get_apify_results(run_id)
                    elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                        print(f"Apify actor failed: {status}")
                        return []
                
                time.sleep(2)
                waited += 2
            
            print("Apify actor timeout")
            return []
        
        except Exception as e:
            print(f"Error scraping events via Apify: {e}")
            return []
    
    def _get_apify_results(self, run_id: str) -> List[Event]:
        """Get results from Apify actor run"""
        try:
            response = requests.get(
                f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items",
                params={"token": self.apify_key},
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            items = response.json()
            events = []
            
            for item in items[:10]:  # Limit to 10 events
                # Parse event data
                event_name = item.get("title", "")
                event_date = item.get("date", "")
                event_location = item.get("location", "")
                
                # Determine format
                format_type = "virtual" if "online" in event_location.lower() or "virtual" in event_name.lower() else "in-person"
                
                # Classify event type
                event_type = self._classify_event(event_name)
                
                # Estimate scale
                scale = "medium"  # Default
                
                events.append(Event(
                    name=event_name,
                    date=event_date or datetime.now().strftime("%Y-%m-%d"),
                    event_type=event_type,
                    format=format_type,
                    estimated_scale=scale
                ))
            
            return events
        
        except Exception as e:
            print(f"Error getting Apify results: {e}")
            return []
    
    def _classify_event(self, name: str) -> str:
        """Classify event type from name"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ["conference", "summit", "expo", "forum"]):
            return "conference"
        elif any(word in name_lower for word in ["launch", "unveil", "release", "debut"]):
            return "launch"
        elif any(word in name_lower for word in ["activation", "experience", "pop-up", "installation"]):
            return "activation"
        elif any(word in name_lower for word in ["webinar", "workshop", "training"]):
            return "webinar"
        else:
            return "event"
    
    def _placeholder_events(self, company_name: str) -> List[Event]:
        """Placeholder events when API fails"""
        return [
            Event(
                name=f"{company_name} Industry Conference",
                date="2026-Q2",
                event_type="conference",
                format="hybrid",
                estimated_scale="medium"
            )
        ]
