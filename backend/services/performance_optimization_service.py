from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
from typing import Optional, Dict, Any
import asyncio
from functools import wraps
import hashlib
import os

# Configure logging
logger = logging.getLogger(__name__)

# Try to import Redis-related modules
try:
    from fastapi_cache import FastAPICache
    from fastapi_cache.backends.redis import RedisBackend
    from fastapi_cache.decorator import cache
    import redis
    import aioredis
    REDIS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Redis modules not available: {e}. Running without Redis cache.")
    REDIS_AVAILABLE = False

class PerformanceOptimizationService:
    def __init__(self):
        self.redis_client = None
        self.cache_enabled = False
        self.compression_enabled = True
        
    async def initialize_cache(self, app: FastAPI):
        """Initialize Redis cache for FastAPI"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available - running without cache")
            self.cache_enabled = False
            return
            
        try:
            # Try to connect to Redis (will fail gracefully if not available)
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            await self.redis_client.ping()
            
            # Initialize FastAPI Cache
            FastAPICache.init(RedisBackend(self.redis_client), prefix="fixmate-cache")
            
            self.cache_enabled = True
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.warning(f"Redis cache initialization failed: {e}. Running without cache.")
            self.cache_enabled = False
            
    def setup_compression(self, app: FastAPI):
        """Setup response compression"""
        if self.compression_enabled:
            # Add GZip compression middleware
            app.add_middleware(GZipMiddleware, minimum_size=1000)
            logger.info("GZip compression enabled")
    
    def setup_caching_headers(self, app: FastAPI):
        """Setup caching headers middleware"""
        @app.middleware("http")
        async def add_cache_headers(request: Request, call_next):
            response = await call_next(request)
            
            # Add cache headers for static content
            if request.url.path.startswith('/static/') or request.url.path.endswith(('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg')):
                # Cache static files for 1 year
                response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
                response.headers["ETag"] = f'"{hashlib.md5(request.url.path.encode()).hexdigest()}"'
            
            # Add cache headers for API responses
            elif request.url.path.startswith('/api/'):
                # Different cache strategies for different endpoints
                if any(path in request.url.path for path in ['/dashboard/', '/users/', '/fixers/']):
                    # Cache user/dashboard data for 5 minutes
                    response.headers["Cache-Control"] = "private, max-age=300"
                elif any(path in request.url.path for path in ['/jobs', '/reviews']):
                    # Cache job/review data for 2 minutes
                    response.headers["Cache-Control"] = "private, max-age=120"
                elif 'tracking' in request.url.path:
                    # Don't cache real-time tracking data
                    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                else:
                    # Default API cache: 1 minute
                    response.headers["Cache-Control"] = "private, max-age=60"
            
            # Security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            return response
    
    def cache_key_builder(self, func_name: str, *args, **kwargs) -> str:
        """Build cache key for function calls"""
        # Create a hash of the function name and arguments
        key_data = {
            'func': func_name,
            'args': str(args),
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return f"func:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def get_cached_response(self, key: str) -> Optional[Any]:
        """Get cached response"""
        if not self.cache_enabled or not self.redis_client:
            return None
            
        try:
            cached_data = await self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Cache read error: {e}")
        
        return None
    
    async def set_cached_response(self, key: str, data: Any, ttl: int = 300):
        """Set cached response"""
        if not self.cache_enabled or not self.redis_client:
            return
            
        try:
            await self.redis_client.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Cache write error: {e}")
    
    async def invalidate_cache_pattern(self, pattern: str):
        """Invalidate cache keys matching pattern"""
        if not self.cache_enabled or not self.redis_client:
            return
            
        try:
            keys = await self.redis_client.keys(f"fixmate-cache:{pattern}")
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys matching pattern: {pattern}")
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    def cached_endpoint(self, ttl: int = 300, key_prefix: str = ""):
        """Decorator for caching endpoint responses"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.cache_enabled:
                    return await func(*args, **kwargs)
                
                # Build cache key
                cache_key = f"{key_prefix}:{self.cache_key_builder(func.__name__, *args, **kwargs)}"
                
                # Try to get from cache
                cached_result = await self.get_cached_response(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set_cached_response(cache_key, result, ttl)
                logger.debug(f"Cache miss, stored result for key: {cache_key}")
                
                return result
            
            return wrapper
        return decorator

# Create global instance
performance_service = PerformanceOptimizationService()

# Decorator functions for easy use
def cache_response(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching responses"""
    return performance_service.cached_endpoint(ttl=ttl, key_prefix=key_prefix)

# Cache decorators for different data types
def cache_user_data(ttl: int = 300):
    """Cache user-related data"""
    return cache_response(ttl=ttl, key_prefix="user")

def cache_job_data(ttl: int = 120):
    """Cache job-related data"""
    return cache_response(ttl=ttl, key_prefix="job")

def cache_fixer_data(ttl: int = 300):
    """Cache fixer-related data"""
    return cache_response(ttl=ttl, key_prefix="fixer")

def cache_dashboard_data(ttl: int = 180):
    """Cache dashboard data"""
    return cache_response(ttl=ttl, key_prefix="dashboard")

def cache_admin_data(ttl: int = 600):
    """Cache admin analytics data"""
    return cache_response(ttl=ttl, key_prefix="admin")

# Database query optimization helpers
class DatabaseOptimizer:
    @staticmethod
    def optimize_query_with_pagination(query, skip: int = 0, limit: int = 20, max_limit: int = 100):
        """Optimize database queries with pagination"""
        # Ensure reasonable limits
        limit = min(limit, max_limit)
        skip = max(0, skip)
        
        return query.offset(skip).limit(limit)
    
    @staticmethod
    def add_eager_loading(query, *relationships):
        """Add eager loading for relationships to prevent N+1 queries"""
        from sqlalchemy.orm import joinedload
        
        for relationship in relationships:
            query = query.options(joinedload(relationship))
        
        return query
    
    @staticmethod
    def optimize_count_query(query):
        """Optimize count queries"""
        from sqlalchemy import func
        
        # Use efficient count query
        return query.statement.with_only_columns([func.count()]).order_by(None)

# Performance monitoring helpers
class PerformanceMonitor:
    @staticmethod
    def time_function(func_name: str = None):
        """Decorator to time function execution"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                import time
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if execution_time > 1.0:  # Log slow queries
                        logger.warning(f"Slow function {func_name or func.__name__}: {execution_time:.2f}s")
                    elif execution_time > 0.5:
                        logger.info(f"Function {func_name or func.__name__}: {execution_time:.2f}s")
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Function {func_name or func.__name__} failed after {execution_time:.2f}s: {e}")
                    raise
                    
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                import time
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if execution_time > 1.0:
                        logger.warning(f"Slow function {func_name or func.__name__}: {execution_time:.2f}s")
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Function {func_name or func.__name__} failed after {execution_time:.2f}s: {e}")
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator

# Batch processing helpers for bulk operations
class BatchProcessor:
    @staticmethod
    async def process_in_batches(items, batch_size: int = 100, processor_func = None):
        """Process items in batches to prevent memory overload"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            if processor_func:
                batch_results = await processor_func(batch)
                results.extend(batch_results)
            else:
                results.extend(batch)
            
            # Small delay to prevent overwhelming the database
            if len(items) > batch_size:
                await asyncio.sleep(0.01)
        
        return results

# Response compression helpers
class ResponseOptimizer:
    @staticmethod
    def compress_json_response(data: dict) -> dict:
        """Optimize JSON responses by removing None values and compressing data"""
        def remove_none_values(obj):
            if isinstance(obj, dict):
                return {k: remove_none_values(v) for k, v in obj.items() if v is not None}
            elif isinstance(obj, list):
                return [remove_none_values(item) for item in obj if item is not None]
            else:
                return obj
        
        return remove_none_values(data)
    
    @staticmethod
    def paginate_response(data: list, total: int, skip: int, limit: int) -> dict:
        """Create paginated response with metadata"""
        return {
            'data': data,
            'pagination': {
                'total': total,
                'skip': skip,
                'limit': limit,
                'has_more': skip + len(data) < total,
                'current_page': (skip // limit) + 1,
                'total_pages': (total + limit - 1) // limit
            }
        }

# Export all optimization utilities
__all__ = [
    'performance_service',
    'cache_response',
    'cache_user_data',
    'cache_job_data',
    'cache_fixer_data',
    'cache_dashboard_data',
    'cache_admin_data',
    'DatabaseOptimizer',
    'PerformanceMonitor',
    'BatchProcessor',
    'ResponseOptimizer'
]