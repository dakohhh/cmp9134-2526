import time
from fastapi import Depends
from urllib.parse import urlparse
from settings.config import SettingsDep
from typing import Annotated, Optional, Dict, Any, Literal
from redis.asyncio import Redis, from_url as redis_from_url

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
    def __init__(self, url: Optional[str] = None):
        self.url = url
        self.default_store: CACHE_STORES = "memory"
        self.redis: Optional[Redis] = None # type: ignore
        self.memory_store: Dict[str, MemoryCacheValue] = {}

    async def connect(self,  **kwargs: Any) -> Any:
        if self.url and is_valid_redis_url(self.url):
            self.redis = await redis_from_url(self.url, **kwargs) # type: ignore
            self.default_store = "redis"
        else:
            self.default_store = "memory"

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

    async def close(self) -> None:
        if self.redis:
            await self.redis.close() # type: ignore


async def get_cache_service(settings: SettingsDep) -> Cache:
    cache_service = Cache(url=settings.REDIS_URL) # type: ignore

    await cache_service.connect(**{"decode_responses": True})
    return cache_service


CacheService = Annotated[Cache, Depends(get_cache_service)]