import redis.asyncio as redis
from app.core.config import settings

class RedisStore:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.cache_ttl = settings.CACHE_TTL_SECONDS

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int = None):
        ttl = ttl or self.cache_ttl
        return await self.client.setex(key, ttl, value)

    async def incr(self, key: str):
        return await self.client.incr(key)

    async def expire(self, key: str, ttl: int):
        return await self.client.expire(key, ttl)

    async def z_incrby(self, key, amount, member):
        return await self.client.zincrby(key, amount, member)

    async def delete(self, key):
        return await self.client.delete(key)

    async def zrevrange(self, key, start, end):
        return await self.client.zrevrange(key, start, end)

    async def incrbyfloat(self, key: str, amount: float):
        return await self.client.incrbyfloat(key, amount)


redis_store = RedisStore()
redis_client = redis_store   # use methods directly
