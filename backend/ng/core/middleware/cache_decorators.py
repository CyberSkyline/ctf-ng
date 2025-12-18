"""Generic Redis caching decorators"""

import functools
from collections.abc import Callable
from ..utils.redis_cache import RedisCache
from ..utils.logger import get_logger

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


def cache_with_args(key_template: str, ttl: int = 300):
    """Cache function result with dynamic key from arguments"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                cache_key = key_template.format(*args, **kwargs)
            except (KeyError, IndexError):
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            cached_result = RedisCache.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            RedisCache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator


