import json
import logging
from typing import Optional, Any
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger(__name__)

import time

_redis_client: Optional[aioredis.Redis] = None
_last_connect_attempt: float = 0.0
_redis_disabled: bool = False

def get_redis_client() -> Optional[aioredis.Redis]:
    """
    Returns Singleton async Redis client instance.
    If Redis is unreachable, caches failure state for 30s to provide instant fallback.
    """
    global _redis_client, _last_connect_attempt, _redis_disabled
    now = time.time()
    if _redis_disabled and (now - _last_connect_attempt) < 30:
        return None

    if _redis_client is None:
        try:
            _last_connect_attempt = now
            _redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=0.2
            )
            _redis_disabled = False
        except Exception as e:
            logger.warning(f"Could not connect to Redis at {settings.REDIS_URL}: {e}")
            _redis_client = None
            _redis_disabled = True
    return _redis_client

async def get_cache(key: str) -> Optional[Any]:
    """
    Retrieves and parses JSON cached data by key. Returns None if key is missing or Redis is down.
    """
    client = get_redis_client()
    if not client:
        return None
    try:
        data = await client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        global _redis_disabled
        _redis_disabled = True
        logger.warning(f"Redis GET failed for key '{key}': {e}")
    return None

async def set_cache(key: str, value: Any, ttl: int = settings.CACHE_TTL_SECONDS) -> bool:
    """
    Serializes data to JSON and stores in Redis with a TTL. Returns True on success.
    """
    client = get_redis_client()
    if not client:
        return False
    try:
        serialized = json.dumps(value, default=str)
        await client.set(key, serialized, ex=ttl)
        return True
    except Exception as e:
        global _redis_disabled
        _redis_disabled = True
        logger.warning(f"Redis SET failed for key '{key}': {e}")
        return False

async def delete_cache(key: str) -> bool:
    """
    Deletes a single cache key.
    """
    client = get_redis_client()
    if not client:
        return False
    try:
        await client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Redis DELETE failed for key '{key}': {e}")
        return False

async def delete_cache_pattern(pattern: str) -> bool:
    """
    Deletes all keys matching a wildcard pattern (e.g. 'events:catalog:*').
    """
    client = get_redis_client()
    if not client:
        return False
    try:
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
        return True
    except Exception as e:
        logger.warning(f"Redis DELETE pattern failed for '{pattern}': {e}")
        return False
