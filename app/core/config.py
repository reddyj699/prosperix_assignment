import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    # Redis Config
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # App Config
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    API_KEY_LIMIT_PER_MIN: int = int(os.getenv("API_KEY_LIMIT_PER_MIN", 5))
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", 3))
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = int(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", 30))
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", 120))

settings = Settings()
