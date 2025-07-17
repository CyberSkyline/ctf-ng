"""
Ctf-ng Cache Decorator
"""

from time import time
from functools import wraps

_cache = {}

def memoize(timeout: int = 60):
    """
    Caching decorator with timeout in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            
            if key in _cache:
                value, timestamp = _cache[key]
                if time() - timestamp < timeout:
                    return value
            
            result = func(*args, **kwargs)
            _cache[key] = (result, time())
            return result
        return wrapper
    return decorator
