from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
import pytest
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.core.db import get_db
from app.domain.base import Base
from app.domain.user import User
from app.domain.link import Link, LinkStats
from app.core.redis import CacheManager, get_cache_manager
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
from app.core.config import settings

# Base de datos en memoria para tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DB_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},  # Necesario para SQLite
)
TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Crear y eliminar el esquema de la base de datos para los tests
@pytest.fixture(scope="session", autouse=True)
async def create_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Fixture para la sesión de la base de datos
@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
        await session.execute(LinkStats.__table__.delete())
        await session.execute(Link.__table__.delete())
        await session.execute(User.__table__.delete())
        await session.commit()


# Fixture para el cliente HTTP asíncrono
@pytest.fixture
async def client(
    db: AsyncSession, monkeypatch
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    # Override Redis host for testing
    settings.REDIS_HOST = "localhost"
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1",
        decode_responses=True,
    )
    
    monkeypatch.setattr("app.services.stats_service.redis_client", redis)
    monkeypatch.setattr("app.core.redis.redis_client", redis)
    monkeypatch.setattr("tests.test_stats.redis_client", redis)

    def override_get_cache_manager() -> CacheManager:
        return CacheManager(redis)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cache_manager] = override_get_cache_manager

    await FastAPILimiter.init(redis)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()
    await redis.flushdb()
    await FastAPILimiter.close()


import uuid

@pytest.fixture
async def db_with_link(db: AsyncSession) -> Link:
    user = User(id=uuid.uuid4(), email="test@test.com", hashed_password="password")
    link = Link(
        id=1,
        short_code="test",
        url="http://test.com",
        user_id=user.id,
        user=user,
    )
    stats = LinkStats(
        id=1,
        link_id=link.id,
        clicks=10,
        countries={"US": 5, "UK": 5},
        link=link,
    )
    db.add(user)
    db.add(link)
    db.add(stats)
    await db.commit()
    return link
