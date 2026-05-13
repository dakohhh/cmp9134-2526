import time
from fastapi import Depends
from urllib.parse import urlparse
from app.common.dependencies import RedisClient
from typing import Annotated, Optional, Dict, Any, Literal

CACHE_STORES = Literal["memory", "redis"]


def is_valid_redis_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in ("redis", "rediss") and
            parsed.hostname is not None and
            (parsed.port is None or 1 <= parsed.port <= 65535)
        )
    except Exception:
        return False

class MemoryCacheValue:
    """
    ttl is in seconds
    """
    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.expiry_time = None
        if ttl:
            self.expiry_time = time.time() + ttl


class Cache:
    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis: Optional[RedisClient] = redis_client 
        self.memory_store: Dict[str, MemoryCacheValue] = {}
        
        self.default_store: CACHE_STORES = "memory"

        if self.redis:
            self.default_store = "redis"

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> Any:
        if self.default_store == "redis" and self.redis:
            await self.redis.set(key, value, ex=ttl)
        else:
            self.memory_store[key] = MemoryCacheValue(value=value, ttl=ttl)

    async def get(self, key: str) -> Optional[Any]:
        if self.default_store == "redis" and self.redis:
            return await self.redis.get(key)
        
        memory_value = self.memory_store.get(key, None)
        if not memory_value:
            return None
        
        # Validate in-memory expiry
        if memory_value.expiry_time and memory_value.expiry_time < time.time():
            # Clear from cache
            self.memory_store.pop(key)
            return None
            
        return memory_value.value
    

    async def delete(self, key: str) -> Optional[Any]:
        if self.default_store == "redis" and self.redis:
            return await self.redis.delete(key)
        return self.memory_store.pop(key, None)


async def get_cache_service(redis_client: RedisClient) -> Cache:
    cache_service = Cache(redis_client=redis_client)

    return cache_service


CacheService = Annotated[Cache, Depends(get_cache_service)]