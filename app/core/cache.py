from redis import asyncio as aioredis
from app.core.config import settings

class CacheManager:
    def __init__(self, cache_instance):
        self.redis = cache_instance

    async def add_to_blacklist(self, token: str, expire_time: int):
        await self.redis.set(token, "blacklisted", ex=expire_time)

    async def is_blacklisted(self, token: str) -> bool:
        return await self.redis.get(token) is not None

def get_cache_manager():
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    )
    return CacheManager(redis)
