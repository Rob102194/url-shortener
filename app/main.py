from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import auth, stats
from app.core.redis import init_redis_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis_pool()
    yield

app = FastAPI(title="URL Shortener API", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(stats.router)

@app.get("/")
def root():
    return {"status": "ok"}
