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

def clear_cache_for_function(func_name: str):
    """
    Clear cache entries for a specific function
    """
    keys_to_delete = [k for k in _cache.keys() if k.startswith(f"{func_name}:")]
    for k in keys_to_delete:
        del _cache[k]

def clear_cache_for_function_with_prefix(func_name: str, prefix: str):
    """
    Clear cache entries for a specific function that match a prefix
    """
    keys_to_delete = []
    for key in _cache.keys():
        if key.startswith(f"{func_name}:{prefix}"):
            keys_to_delete.append(key)
    for key in keys_to_delete:
        del _cache[key]
