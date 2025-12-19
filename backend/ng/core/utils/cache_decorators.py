"""Generic Redis caching decorators"""

import functools
from collections.abc import Callable
from .redis_cache import RedisCache
from .logger import get_logger

logger = get_logger(__name__)


def cache(key: str, ttl: int = 300):
    """Cache function result with static key"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cached_result = RedisCache.get(key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            RedisCache.set(key, result, ttl)
            return result

        return wrapper
    return decorator


def cache_with_args(key: str = None, ttl: int = 300):
    """Cache function result with static key, or override with 'cache_key' kwarg at call time."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = kwargs.get('cache_key', None)
            if cache_key is None:
                raise TypeError("No cache key provided.")
            cached_result = RedisCache.get(cache_key)
            if cached_result is not None:
                return cached_result
            result = func(*args, **kwargs)
            RedisCache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


