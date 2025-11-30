
from app.core.redis_clinet import redis_client
from app.core.config import settings


from functools import wraps
from fastapi import HTTPException
from app.models.request_model import SKUModel


def validate_api_key(route_handler):
    @wraps(route_handler)
    async def wrapper(*args, x_api_key: str = None, **kwargs):

        if not x_api_key:
            raise HTTPException(status_code=400, detail="Missing X-API-Key header")

        # Optional: you can validate API-key from DB/Redis/settings

        return await route_handler(*args, x_api_key=x_api_key, **kwargs)

    return wrapper




def rate_limit(route_handler):
    @wraps(route_handler)
    async def wrapper(*args, x_api_key: str = None, **kwargs):
        key = f"ratelimit:{x_api_key}"
        current = await redis_client.incr(key)

        if current == 1:
            redis_client.expire(key, 60)

        if current > settings.API_KEY_LIMIT_PER_MIN:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        return await route_handler(*args, x_api_key=x_api_key, **kwargs)

    return wrapper



def validate_sku(route_handler):
    @wraps(route_handler)
    async def wrapper(sku: str, *args, **kwargs):
        try:
            SKUModel(sku=sku)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid SKU")

        return await route_handler(sku, *args, **kwargs)

    return wrapper
