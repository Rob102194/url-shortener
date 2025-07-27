from redis import asyncio as aioredis
from fastapi_limiter import FastAPILimiter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from app.core.config import settings

redis_client = None

async def init_redis_pool():
    global redis_client
    redis_client = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf-8",
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    await FastAPILimiter.init(redis_client)

class CacheManager:
    def __init__(self, cache_instance):
        self.redis = cache_instance

    def add_to_blacklist(self, token: str, expire_time: int):
        return self.redis.set(token, "blacklisted", ex=expire_time)

    def is_blacklisted(self, token: str):
        return self.redis.get(token)

def get_cache_manager():
    return CacheManager(redis_client)
