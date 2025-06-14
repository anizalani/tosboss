from functools import wraps
import asyncio
import time
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Advanced rate limiter with domain-specific limits"""
    
    def __init__(self):
        self.request_times: Dict[str, list] = {}
        self.domain_limits: Dict[str, int] = {}
    
    def set_domain_limit(self, domain: str, requests_per_minute: int):
        """Set rate limit for specific domain"""
        self.domain_limits[domain] = requests_per_minute
    
    async def wait_if_needed(self, domain: str):
        """Wait if rate limit is reached"""
        limit = self.domain_limits.get(domain, 3)  # Default: 3 requests per minute
        
        current_time = time.time()
        if domain not in self.request_times:
            self.request_times[domain] = []
        
        # Clean old requests
        self.request_times[domain] = [t for t in self.request_times[domain] 
                                    if current_time - t < 60]
        
        if len(self.request_times[domain]) >= limit:
            wait_time = 60 - (current_time - self.request_times[domain][0])
            if wait_time > 0:
                logger.info(f"Rate limit reached for {domain}, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
        
        self.request_times[domain].append(current_time)

def rate_limited(f):
    """Decorator for rate-limited functions"""
    @wraps(f)
    async def wrapped(self, *args, **kwargs):
        await self.rate_limiter.wait_if_needed(self.domain)
        return await f(self, *args, **kwargs)
    return wrapped