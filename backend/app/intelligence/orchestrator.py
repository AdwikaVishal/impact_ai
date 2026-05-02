"""
Intelligence Orchestrator
Coordinates all intelligence modules to generate complete reports
"""
from datetime import datetime
from typing import Dict
import hashlib
import json
from .models import CompanyInput, CompanyIntelligence, Event
from .company_profiler import CompanyProfiler
from .competitor_mapper import CompetitorMapper
from .brand_analyzer import BrandAnalyzer
from .activity_tracker import ActivityTracker
from .strategic_analyzer import StrategicAnalyzer
from .outreach_generator import OutreachGenerator

# Import new modules
from .decision_maker_finder_v2 import DecisionMakerFinder
from .events_tracker import EventsTracker

# Import cache and feature flags
from app.core.cache import cache
from app.core.feature_flags import feature_flags


class IntelligenceOrchestrator:
    """Orchestrate all intelligence gathering modules"""
    
    def __init__(self):
        self.profiler = CompanyProfiler()
        self.competitor_mapper = CompetitorMapper()
        self.brand_analyzer = BrandAnalyzer()
        self.activity_tracker = ActivityTracker()
        self.strategic_analyzer = StrategicAnalyzer()
        self.decision_maker_finder = DecisionMakerFinder()
        self.events_tracker = EventsTracker()
        self.outreach_generator = OutreachGenerator()
        
        # Cache configuration
        self.cache_enabled = feature_flags.is_enabled('cache_enabled')
        self.use_prospeo = feature_flags.is_enabled('use_prospeo_api')
        self.use_apify = feature_flags.is_enabled('use_apify_events')
        
        if self.cache_enabled:
            print("🚀 Cache optimization enabled")
        if self.use_prospeo:
            print("🚀 Prospeo API integration enabled")
        if self.use_apify:
            print("🚀 Apify events tracking enabled")
    
    def _generate_cache_key(self, company_name: str, category: str, opportunity_angle: str) -> str:
        """Generate cache key for intelligence report"""
        key_data = f"intelligence:{company_name}:{category}:{opportunity_angle}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def generate_intelligence(
        self,
        company_input: CompanyInput,
        opportunity_angle: str = "marketing technology partnership"
    ) -> CompanyIntelligence:
        """
        Generate complete intelligence report with caching
        """
        company_name = company_input.company_name
        category = company_input.category
        
        print(f"🔍 Generating intelligence for {company_name}...")
        
        # Check cache first
        if self.cache_enabled and feature_flags.is_enabled('cache_intelligence_reports'):
            cache_key = self._generate_cache_key(company_name, category, opportunity_angle)
            cached_data = cache.get(cache_key)
            
            if cached_data:
                print("⚡ Using cached intelligence report")
                # Convert dict back to CompanyIntelligence object
                cached_data['generated_at'] = datetime.fromisoformat(cached_data['generated_at'])
                return CompanyIntelligence(**cached_data)
        
        # Generate fresh intelligence
        print("🔄 Generating fresh intelligence report...")
        
        # 1. Company Overview
        print("📊 Profiling company...")
        profile = self._cached_profile(company_name, category)
        
        # 2. Market Position
        print("🎯 Analyzing brand...")
        brand_analysis = self.brand_analyzer.analyze_brand(company_name)
        
        # 3. Competitor Mapping
        print("🏆 Mapping competitors...")
        competitors = self._cached_competitors(company_name, category)
        
        # 4. Brand Activity
        print("📅 Tracking activities...")
        activities = self.activity_tracker.track_activities(company_name, months=12)
        
        # 5. Events Footprint - Use Apify if enabled
        print("🎪 Analyzing events...")
        if self.use_apify:
            events = self.events_tracker.track_events(company_name)
        else:
            events = self._generate_events_placeholder(company_name)
        
        # 6. Strategic Watchouts
        print("⚠️  Identifying watchouts...")
        watchouts = self.strategic_analyzer.analyze_watchouts(company_name, category)
        
        # 7-8. Decision Makers & Contacts - Use Prospeo if enabled
        print("👥 Finding decision makers...")
        decision_makers = self._cached_decision_makers(company_name, category, competitors)
        
        # 9. Personalized Outreach
        print("✉️  Generating outreach messages...")
        outreach_messages = {}
        
        if decision_makers:
            # Generate for top decision maker
            top_dm = decision_makers[0]
            
            # Create temporary intelligence object for outreach generation
            temp_intelligence = CompanyIntelligence(
                company_name=company_name,
                category=category,
                business_model=profile["business_model"],
                positioning=profile["positioning"],
                scale_metrics=profile["scale_metrics"],
                brand_perception=brand_analysis["brand_perception"],
                recent_shifts=brand_analysis["recent_shifts"],
                competitors=competitors,
                activities=activities,
                events=events,
                watchouts=watchouts,
                decision_makers=decision_makers,
                outreach_messages={},
                generated_at=datetime.now(),
                confidence_score=0.0
            )
            
            outreach_messages = self.outreach_generator.generate_outreach(
                top_dm, temp_intelligence, opportunity_angle
            )
        
        # Calculate confidence score
        confidence = self._calculate_confidence(
            profile, competitors, activities, decision_makers
        )
        
        print(f"✅ Intelligence report generated (confidence: {confidence:.0%})")
        
        # Build final report
        intelligence = CompanyIntelligence(
            company_name=company_name,
            category=category,
            business_model=profile["business_model"],
            positioning=profile["positioning"],
            scale_metrics=profile["scale_metrics"],
            brand_perception=brand_analysis["brand_perception"],
            recent_shifts=brand_analysis["recent_shifts"],
            competitors=competitors,
            activities=activities,
            events=events,
            watchouts=watchouts,
            decision_makers=decision_makers,
            outreach_messages=outreach_messages,
            generated_at=datetime.now(),
            confidence_score=confidence
        )
        
        # Cache the result
        if self.cache_enabled and feature_flags.is_enabled('cache_intelligence_reports'):
            cache_key = self._generate_cache_key(company_name, category, opportunity_angle)
            # Convert to dict for caching
            cache_data = intelligence.dict()
            cache_data['generated_at'] = cache_data['generated_at'].isoformat()
            cache.set(cache_key, cache_data, cache.ttls['intelligence_report'])
            print("💾 Intelligence report cached")
        
        return intelligence
    
    def _cached_profile(self, company_name: str, category: str) -> Dict:
        """Get company profile with caching"""
        if self.cache_enabled and feature_flags.is_enabled('cache_company_profiles'):
            cache_key = f"profile:{hashlib.md5(f'{company_name}:{category}'.encode()).hexdigest()}"
            cached = cache.get(cache_key)
            if cached:
                print("⚡ Using cached profile")
                return cached
        
        # Generate fresh
        profile = self.profiler.profile_company(company_name, category)
        
        # Cache it
        if self.cache_enabled and feature_flags.is_enabled('cache_company_profiles'):
            cache.set(cache_key, profile, cache.ttls['company_profile'])
        
        return profile
    
    def _cached_competitors(self, company_name: str, category: str) -> list:
        """Get competitors with caching"""
        if self.cache_enabled and feature_flags.is_enabled('cache_competitors'):
            cache_key = f"competitors:{hashlib.md5(f'{company_name}:{category}'.encode()).hexdigest()}"
            cached = cache.get(cache_key)
            if cached:
                print("⚡ Using cached competitors")
                return cached
        
        # Generate fresh
        competitors = self.competitor_mapper.discover_competitors(company_name, category)
        competitors = self.competitor_mapper.analyze_competitor_strengths(competitors)
        
        # Cache it
        if self.cache_enabled and feature_flags.is_enabled('cache_competitors'):
            cache.set(cache_key, competitors, cache.ttls['competitors'])
        
        return competitors
    
    def _cached_decision_makers(self, company_name: str, category: str, competitors: list) -> list:
        """Get decision makers with caching"""
        if self.cache_enabled and feature_flags.is_enabled('cache_decision_makers'):
            cache_key = f"decision_makers:{hashlib.md5(company_name.encode()).hexdigest()}"
            cached = cache.get(cache_key)
            if cached:
                print("⚡ Using cached decision makers")
                return cached
        
        # Generate fresh
        decision_makers = []
        
        # Try to find decision makers for the company
        if competitors:
            domain = self._extract_domain(company_name)
            decision_makers = self.decision_maker_finder.find_decision_makers(
                company_name, domain, category
            )
            decision_makers = self.decision_maker_finder.enrich_with_linkedin(
                decision_makers, company_name
            )
        
        # If no decision makers found, use fallback
        if not decision_makers:
            decision_makers = self.decision_maker_finder._fallback_decision_makers(
                company_name, category
            )
        
        # Cache it
        if self.cache_enabled and feature_flags.is_enabled('cache_decision_makers'):
            cache.set(cache_key, decision_makers, cache.ttls['decision_makers'])
        
        return decision_makers
    
    def _extract_domain(self, company_name: str) -> str:
        """Extract likely domain from company name"""
        # Simple heuristic: company name + .com
        domain = company_name.lower().replace(" ", "").replace(",", "").replace(".", "")
        return f"{domain}.com"
    
    def _generate_events_placeholder(self, company_name: str) -> list:
        """Generate placeholder events (can be enhanced with real event tracking)"""
        return [
            Event(
                name=f"{company_name} Annual Conference",
                date="2026-Q2",
                event_type="conference",
                format="hybrid",
                estimated_scale="medium"
            )
        ]
    
    def _calculate_confidence(
        self,
        profile: Dict,
        competitors: list,
        activities: list,
        decision_makers: list
    ) -> float:
        """Calculate confidence score based on data availability"""
        score = 0.0
        
        # Profile data (30%)
        if profile["business_model"] and len(profile["business_model"]) > 50:
            score += 0.15
        if profile["positioning"] and len(profile["positioning"]) > 50:
            score += 0.15
        
        # Competitors (20%)
        if competitors:
            score += min(0.20, len(competitors) * 0.05)
        
        # Activities (20%)
        if activities:
            score += min(0.20, len(activities) * 0.02)
        
        # Decision makers (30%)
        if decision_makers:
            score += min(0.30, len(decision_makers) * 0.10)
        
        return min(1.0, score)
