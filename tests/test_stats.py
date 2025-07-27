import pytest
from httpx import AsyncClient
from app.domain.link import Link, LinkStats
from app.core.redis import redis_client
import json

pytestmark = pytest.mark.asyncio

async def test_get_stats_not_cached(client: AsyncClient, db_with_link):
    res = await client.get(f"/stats/{db_with_link.short_code}")
    assert res.status_code == 200
    data = res.json()
    assert data["clicks"] == 10
    assert data["countries"] == {"US": 5, "UK": 5}

async def test_get_stats_cached(client: AsyncClient, db_with_link):
    # First request to cache the stats
    await client.get(f"/stats/{db_with_link.short_code}")

    # Second request should hit the cache
    res = await client.get(f"/stats/{db_with_link.short_code}")
    assert res.status_code == 200
    data = res.json()
    assert data["clicks"] == 10
    assert data["countries"] == {"US": 5, "UK": 5}

async def test_invalidate_stats_cache(client: AsyncClient, db_with_link):
    # First request to cache the stats
    await client.get(f"/stats/{db_with_link.short_code}")

    # Invalidate the cache
    res = await client.post(f"/stats/{db_with_link.short_code}/click")
    assert res.status_code == 200

    # Check that the cache is empty
    cached = await redis_client.get(f"stats:{db_with_link.short_code}")
    assert cached is None
