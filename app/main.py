from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from app.api import auth
from redis import asyncio as aioredis
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield

app = FastAPI(title="URL Shortener API", lifespan=lifespan)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "ok"}
