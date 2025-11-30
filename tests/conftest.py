import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from app.main import app
from app.utils.redis import get_redis
import redis.asyncio as redis
from unittest.mock import MagicMock, AsyncMock

# Mock Redis for tests to avoid needing a real instance
@pytest.fixture
def mock_redis():
    mock = MagicMock(spec=redis.Redis)
    # Setup common async methods
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.incr = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=True)
    mock.zincrby = AsyncMock(return_value=1)
    mock.zrevrange = AsyncMock(return_value=[])
    # Async context manager for pipeline if needed (not used in simple tests but good practice)
    return mock

@pytest_asyncio.fixture
async def override_get_redis(mock_redis):
    async def _get_redis():
        return mock_redis
    app.dependency_overrides[get_redis] = _get_redis
    return mock_redis

@pytest_asyncio.fixture
async def client(override_get_redis):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
