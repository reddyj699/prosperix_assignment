import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_product_no_auth(client: AsyncClient):
    response = await client.get("/products/123")
    assert response.status_code == 422 # Missing header

@pytest.mark.asyncio
async def test_get_product_invalid_sku(client: AsyncClient):
    response = await client.get("/products/ab", headers={"x-api-key": "test"})
    assert response.status_code == 400 # Too short

@pytest.mark.asyncio
async def test_get_product_success(client: AsyncClient, mock_redis):
    # Mock redis get to return None (cache miss)
    async def mock_get(key):
        return None
    mock_redis.get.side_effect = mock_get

    response = await client.get("/products/validsku", headers={"x-api-key": "test"})
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "validsku"
    assert "status" in data
    assert "best_vendor" in data
    assert len(data["vendors"]) == 3
