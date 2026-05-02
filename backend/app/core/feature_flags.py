"""
Feature Flags System
Safe rollout of new features with graceful degradation
"""
import os
from typing import Dict


class FeatureFlags:
    """Manage feature flags for safe rollout"""
    
    def __init__(self):
        # Load from environment variables
        self.flags = {
            # Cache features
            'cache_enabled': self._get_bool('FEATURE_CACHE_ENABLED', True),
            'cache_intelligence_reports': self._get_bool('FEATURE_CACHE_INTELLIGENCE', True),
            'cache_company_profiles': self._get_bool('FEATURE_CACHE_PROFILES', True),
            'cache_competitors': self._get_bool('FEATURE_CACHE_COMPETITORS', True),
            'cache_decision_makers': self._get_bool('FEATURE_CACHE_DECISION_MAKERS', True),
            
            # New API integrations
            'use_prospeo_api': self._get_bool('FEATURE_USE_PROSPEO', True),
            'use_apify_events': self._get_bool('FEATURE_USE_APIFY', True),
            
            # Performance features
            'parallel_processing': self._get_bool('FEATURE_PARALLEL_PROCESSING', False),
            
            # Monitoring
            'detailed_logging': self._get_bool('FEATURE_DETAILED_LOGGING', True),
        }
    
    def _get_bool(self, key: str, default: bool) -> bool:
        """Get boolean from environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def is_enabled(self, feature: str) -> bool:
        """Check if feature is enabled"""
        return self.flags.get(feature, False)
    
    def get_all(self) -> Dict[str, bool]:
        """Get all feature flags"""
        return self.flags.copy()


# Global feature flags instance
feature_flags = FeatureFlags()
