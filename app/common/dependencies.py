import httpx
from typing import Annotated
from redis.asyncio import Redis
from fastapi import Request, Depends


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_async_client # type: ignore

def get_redis_client(request: Request) -> Redis:
    return request.app.state.redis_client # type: ignore


HttpClient = Annotated[httpx.AsyncClient, Depends(get_http_client)]

RedisClient = Annotated[Redis, Depends(get_redis_client)]
