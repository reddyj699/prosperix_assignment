import logging
import asyncio
from functools import wraps
from app.core.redis_clinet import redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = None, recovery_timeout: int = None):
        self.name = name
        self.failure_threshold = failure_threshold or settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD
        self.recovery_timeout = recovery_timeout or settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT
        self.redis_key_state = f"cb:{name}:state"
        self.redis_key_failures = f"cb:{name}:failures"

    async def call(self, func, *args, **kwargs):

        state = await redis_client.get(self.redis_key_state)

        if state == "OPEN":
            logger.warning(f"Circuit Breaker {self.name} is OPEN. Skipping call.")
            raise CircuitBreakerOpenException(f"Circuit Breaker {self.name} is OPEN")

        try:
            result = await func(*args, **kwargs)
            # Success
            if state == "HALF-OPEN":
                await self._close_circuit(redis_client)
            return result
        except Exception as e:
            await self._record_failure(redis_client)
            raise e

    async def _record_failure(self, redis_client):
        failures = await redis_client.incr(self.redis_key_failures)
        if failures >= self.failure_threshold:
            await self._open_circuit(redis_client)

    async def _open_circuit(self, redis_client):
        logger.warning(f"Circuit Breaker {self.name} opening due to failures.")
        await redis_client.set(self.redis_key_state, "OPEN", ex=self.recovery_timeout)
    async def _close_circuit(self, redis_client):
        logger.info(f"Circuit Breaker {self.name} closing.")
        await redis_client.delete(self.redis_key_state)
        await redis_client.delete(self.redis_key_failures)

def circuit_breaker(name: str):
    def decorator(func):
        cb = CircuitBreaker(name)
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)
        return wrapper
    return decorator
