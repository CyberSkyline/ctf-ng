"""
Generic Redis caching utility
"""

import json
import time
import redis
from typing import Any
from collections.abc import Callable
from flask import current_app
from .logger import get_logger
from ...config import (
    REDIS_SOCKET_CONNECT_TIMEOUT, REDIS_SOCKET_TIMEOUT, REDIS_SOCKET_KEEPALIVE,
    REDIS_MAX_CONNECTIONS, REDIS_RETRY_ON_TIMEOUT, REDIS_MAX_RETRIES, REDIS_RETRY_DELAY
)


logger = get_logger(__name__)


class RedisCache:
    """Generic Redis caching utility with persistent connections and retry logic"""

    _connection_pool = None
    _client = None
    _last_config_hash = None

    @classmethod
    def _get_config_hash(cls) -> str:
        """Generate a hash of the current Redis configuration"""
        try:
            config_str = f"{current_app.config.get('REDIS_URL', '')}" \
                        f"{current_app.config.get('REDIS_HOST', 'localhost')}" \
                        f"{current_app.config.get('REDIS_PORT', 6379)}" \
                        f"{current_app.config.get('REDIS_DB', 0)}" \
                        f"{current_app.config.get('REDIS_PASSWORD', '')}"
            return str(hash(config_str))
        except Exception:
            return "default"

    @classmethod
    def _initialize_client(cls) -> bool:
        """Initialize Redis client with connection pooling"""
        try:
            config_hash = cls._get_config_hash()

            # Reinit if config changed
            if cls._last_config_hash != config_hash:
                cls._client = None
                cls._connection_pool = None
                cls._last_config_hash = config_hash

            if cls._client is not None: # Already connected
                return True

            redis_url = current_app.config.get('REDIS_URL')
            if redis_url:
                cls._connection_pool = redis.ConnectionPool.from_url(
                    redis_url,
                    decode_responses = True,
                    socket_connect_timeout = current_app.config.get('REDIS_SOCKET_CONNECT_TIMEOUT', REDIS_SOCKET_CONNECT_TIMEOUT),
                    socket_timeout = current_app.config.get('REDIS_SOCKET_TIMEOUT', REDIS_SOCKET_TIMEOUT),
                    socket_keepalive = current_app.config.get('REDIS_SOCKET_KEEPALIVE', REDIS_SOCKET_KEEPALIVE),
                    socket_keepalive_options = {},
                    max_connections = current_app.config.get('REDIS_MAX_CONNECTIONS', REDIS_MAX_CONNECTIONS),
                    retry_on_timeout = current_app.config.get('REDIS_RETRY_ON_TIMEOUT', REDIS_RETRY_ON_TIMEOUT)
                )
            else:
                cls._connection_pool = redis.ConnectionPool(
                    host = current_app.config.get('REDIS_HOST', 'localhost'),
                    port = current_app.config.get('REDIS_PORT', 6379),
                    db = current_app.config.get('REDIS_DB', 0),
                    password = current_app.config.get('REDIS_PASSWORD'),
                    decode_responses = True,
                    socket_connect_timeout = current_app.config.get('REDIS_SOCKET_CONNECT_TIMEOUT', REDIS_SOCKET_CONNECT_TIMEOUT),
                    socket_timeout = current_app.config.get('REDIS_SOCKET_TIMEOUT', REDIS_SOCKET_TIMEOUT),
                    socket_keepalive = current_app.config.get('REDIS_SOCKET_KEEPALIVE', REDIS_SOCKET_KEEPALIVE),
                    socket_keepalive_options = {},
                    max_connections = current_app.config.get('REDIS_MAX_CONNECTIONS', REDIS_MAX_CONNECTIONS),
                    retry_on_timeout = current_app.config.get('REDIS_RETRY_ON_TIMEOUT', REDIS_RETRY_ON_TIMEOUT)
                )

            cls._client = redis.Redis(connection_pool=cls._connection_pool)

            # Test connection
            cls._client.ping()
            logger.info("Redis client initialized successfully with connection pooling")
            return True

        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {e}")
            cls._client = None
            cls._connection_pool = None
            return False

    @classmethod
    def _execute_with_retry(cls, operation: Callable) -> Any:
        """Execute Redis operation with retry and reconnection logic"""
        max_retries = current_app.config.get('REDIS_MAX_RETRIES', REDIS_MAX_RETRIES)
        retry_delay = current_app.config.get('REDIS_RETRY_DELAY', REDIS_RETRY_DELAY)

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                # Initialize client if needed
                if not cls._initialize_client():
                    return None

                return operation(cls._client)

            except (redis.ConnectionError, redis.TimeoutError, OSError) as e:
                last_exception = e
                logger.warning(f"Redis connection error (attempt {attempt + 1}/{max_retries + 1}): {e}")

                # Reset client to force reconnection on next attempt
                cls._client = None
                cls._connection_pool = None

                if attempt < max_retries:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff

            except Exception as e:
                logger.warning(f"Redis operation error: {e}")
                return None

        logger.error(f"Redis operation failed after {max_retries + 1} attempts. Last error: {last_exception}")
        return None

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a value from Redis cache"""
        def _get_operation(client):
            value = client.get(key)
            if value is None:
                return default

            # Try to parse as JSON, fall back to string
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        result = cls._execute_with_retry(_get_operation)
        if result is not None:
            return result
        else:
            return default

    @classmethod
    def set(cls, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set a value in Redis cache with optional TTL"""
        def _set_operation(client):
            # Serialize value if it's not a string
            if isinstance(value, str):
                cache_value = value
            else:
                cache_value = json.dumps(value)

            if ttl:
                result = client.setex(key, ttl, cache_value)
            else:
                result = client.set(key, cache_value)

            return bool(result)

        result = cls._execute_with_retry(_set_operation)
        return bool(result) if result is not None else False

    @classmethod
    def delete(cls, key: str) -> bool:
        """Delete a key from Redis cache"""
        def _delete_operation(client):
            return bool(client.delete(key))

        result = cls._execute_with_retry(_delete_operation)
        return bool(result) if result is not None else False

    @classmethod
    def exists(cls, key: str) -> bool:
        """Check if a key exists in Redis cache"""
        def _exists_operation(client):
            return bool(client.exists(key))

        result = cls._execute_with_retry(_exists_operation)
        return bool(result) if result is not None else False

    @classmethod
    def reset_connection(cls):
        """Force reset of Redis connection (useful for testing or recovery)"""
        cls._client = None
        cls._connection_pool = None
        logger.info("Redis connection reset")
