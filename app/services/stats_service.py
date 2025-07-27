import json
import logging
from redis.asyncio import RedisError
from app.core.redis import redis_client
from app.repositories.stats_repo import StatsRepository

CACHE_TTL = 30  # segundos

class StatsService:
    def __init__(self, repo: StatsRepository):
        self.repo = repo

    async def get_stats(self, short_code: str) -> dict:
        key = f"stats:{short_code}"
        try:
            cached = await redis_client.get(key)
            if cached:
                return json.loads(cached)
        except RedisError as e:
            logging.warning(f"Redis GET error: {e}. Falling back to database.")

        # Si no está en caché o Redis falla, calcular desde la BD
        row = await self.repo.fetch_stats(short_code)
        if not row:
            return {"clicks": 0, "countries": {}}
            
        data = {"clicks": row.clicks, "countries": row.countries}
        
        try:
            await redis_client.set(key, json.dumps(data), ex=CACHE_TTL)
        except RedisError as e:
            logging.warning(f"Redis SET error: {e}. Proceeding without caching.")
            
        return data

    # Invalidar el caché para un short_code específico
    async def invalidate_stats_cache(self, short_code: str):
        key = f"stats:{short_code}"
        try:
            await redis_client.delete(key)
        except RedisError as e:
            logging.warning(f"Redis DELETE error: {e}. Cache invalidation failed.")
