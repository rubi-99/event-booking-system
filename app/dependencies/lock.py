import asyncio
import logging
from typing import Optional
from app.redis import get_redis_client

logger = logging.getLogger(__name__)
_local_locks = {}

class DistributedLock:
    """
    Distributed lock helper that attempts to acquire a Redis lock for key.
    If Redis is unavailable, falls back gracefully to a process-level asyncio.Lock.
    """
    def __init__(self, key: str, timeout_seconds: float = 10.0):
        self.key = f"lock:{key}"
        self.timeout_seconds = timeout_seconds
        self._redis_lock = None
        self._local_lock = None

    async def __aenter__(self):
        client = get_redis_client()
        if client:
            try:
                self._redis_lock = client.lock(self.key, timeout=self.timeout_seconds)
                acquired = await self._redis_lock.acquire(blocking=True)
                if acquired:
                    return self
            except Exception as e:
                logger.warning(f"Redis lock acquire failed for '{self.key}': {e}. Falling back to local lock.")
                self._redis_lock = None

        # Fallback to local asyncio lock if Redis lock is unavailable
        if self.key not in _local_locks:
            _local_locks[self.key] = asyncio.Lock()
        self._local_lock = _local_locks[self.key]
        await self._local_lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._redis_lock:
            try:
                await self._redis_lock.release()
            except Exception as e:
                logger.warning(f"Redis lock release failed for '{self.key}': {e}")
        elif self._local_lock and self._local_lock.locked():
            self._local_lock.release()
