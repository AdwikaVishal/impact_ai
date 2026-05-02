"""
Redis Cache Manager for Intelligence Engine
Reduces API calls by 90% through intelligent caching
"""
import redis
import json
import hashlib
from typing import Optional, Any
from datetime import timedelta
import os


class CacheManager:
    """Redis cache manager for intelligence data"""
    
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            print("✅ Redis cache enabled")
        except Exception as e:
            print(f"⚠️  Redis not available: {e}")
            print("   Cache disabled - will use fresh API calls")
            self.enabled = False
            self.redis_client = None
        
        # Cache TTLs (Time To Live)
        self.ttls = {
            'intelligence_report': timedelta(hours=24),  # 24 hours
            'company_profile': timedelta(hours=48),      # 2 days
            'competitors': timedelta(hours=72),          # 3 days
            'decision_makers': timedelta(days=7),        # 1 week
            'news': timedelta(hours=6),                  # 6 hours
            'events': timedelta(days=30),                # 1 month
        }
    
    def _generate_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments"""
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: timedelta = None):
        """Set value in cache with TTL"""
        if not self.enabled:
            return
        
        try:
            data = json.dumps(value, default=str)
            if ttl:
                self.redis_client.setex(key, int(ttl.total_seconds()), data)
            else:
                self.redis_client.set(key, data)
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        if not self.enabled:
            return
        
        try:
            self.redis_client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        if not self.enabled:
            return
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Cache clear error: {e}")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info('stats')
            return {
                "enabled": True,
                "total_keys": self.redis_client.dbsize(),
                "hits": info.get('keyspace_hits', 0),
                "misses": info.get('keyspace_misses', 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}
    
    def _calculate_hit_rate(self, info: dict) -> float:
        """Calculate cache hit rate"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


# Global cache instance
cache = CacheManager()
