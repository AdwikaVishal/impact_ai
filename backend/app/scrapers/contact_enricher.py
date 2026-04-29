"""
Contact Enricher - Guesses emails and enriches contact information
"""

import re
from typing import List, Dict, Optional

def guess_email(name: str, domain: str) -> Optional[str]:
    """
    Guess email address from name and company domain.
    
    Patterns tried:
    - first.last@domain
    - first@domain
    - firstl@domain
    """
    if not name or not domain:
        return None
    
    # Clean domain (remove http://, https://, www.)
    domain = re.sub(r'^https?://(www\.)?', '', domain)
    domain = domain.split('/')[0]  # Remove path
    
    # Clean name
    name = name.lower().strip()
    # Remove anything in parentheses and numbers
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'[^a-z\s]', '', name)
    name = name.strip()
    
    if not name:
        return None
    
    # Split name into parts
    parts = name.split()
    
    if len(parts) == 1:
        # Single name: first@domain
        return f"{parts[0]}@{domain}"
    
    # Two or more parts: first.last@domain
    first = parts[0]
    last = parts[-1]
    
    # Return the most common pattern (first.last)
    return f"{first}.{last}@{domain}"

async def enrich_contacts(people: List[Dict], domain: str, company_name: str) -> List[Dict]:
    """
    Enrich people data with email addresses and clean LinkedIn URLs.
    
    Args:
        people: List from people_scraper with keys: name, role, linkedin_url
        domain: Company domain (e.g., "stripe.com")
        company_name: For logging
    
    Returns:
        List of enriched contacts with name, role, email, linkedin_url, confidence
    """
    enriched = []
    
    for person in people:
        name = person.get("name")
        role = person.get("role", "Marketing Professional")
        linkedin_url = person.get("linkedin_url")
        
        # Try to extract name from LinkedIn URL if missing
        if not name and linkedin_url:
            name = _extract_name_from_linkedin_url(linkedin_url)
        
        # Guess email
        email = guess_email(name, domain) if name and domain else None
        
        # Determine confidence
        confidence = "low"
        if email and name:
            confidence = "medium"
        if linkedin_url and "linkedin.com/in/" in str(linkedin_url):
            confidence = "high" if email else "medium"
        
        enriched.append({
            "name": name or "Unknown",
            "role": role,
            "linkedin_url": linkedin_url or "Not found",
            "email": email or "Not publicly available",
            "confidence": confidence
        })
    
    return enriched

def _extract_name_from_linkedin_url(url: str) -> Optional[str]:
    """Extract person name from LinkedIn profile URL."""
    if not url:
        return None
    
    match = re.search(r'/in/([^/?]+)', url)
    if match:
        name_slug = match.group(1)
        # Convert hyphens/underscores to spaces and capitalize
        name = name_slug.replace('-', ' ').replace('_', ' ')
        name = ' '.join([p.capitalize() for p in name.split()[:2]])
        if len(name) > 2:
            return name
    return None