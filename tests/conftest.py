from typing import AsyncGenerator
import pytest, asyncio
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
import pytest, asyncio
from httpx import AsyncClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.core.db import get_db
from app.domain.base import Base
from app.core.cache import CacheManager, get_cache_manager

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


# Mock CacheManager
class MockCacheManager(CacheManager):
    def __init__(self):
        self.cache = {}

    async def add_to_blacklist(self, token: str, expire_time: int):
        self.cache[token] = "blacklisted"

    async def is_blacklisted(self, token: str) -> bool:
        return token in self.cache

@pytest.fixture
def mock_cache() -> MockCacheManager:
    return MockCacheManager()

# Fixture para el cliente HTTP asíncrono
@pytest.fixture
async def client(
    db: AsyncSession, mock_cache: MockCacheManager
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    def override_get_cache_manager() -> MockCacheManager:
        return mock_cache

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cache_manager] = override_get_cache_manager
    
    # Desactivar el contexto de vida útil de la aplicación para evitar problemas con la conexión a la base de datos
    app.router.lifespan_context = None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()
