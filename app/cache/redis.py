import json
from typing import Any, Optional
import redis
from datetime import timedelta

from app.core.config import settings

class RedisService:
    def __init__(self):
        self._redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            value = self._redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Redis get error for {key}: {str(e)}")
            return None

    async def set(self, key: str, value: Any, expire_minutes: int = 5) -> bool:
        """Set value in Redis cache with expiration"""
        try:
            return self._redis.setex(
                name=key,
                time=timedelta(minutes=expire_minutes),
                value=json.dumps(value)
            )
        except Exception as e:
            print(f"Redis set error for {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""
        try:
            return bool(self._redis.delete(key))
        except Exception as e:
            print(f"Redis delete error for {key}: {str(e)}")
            return False

    async def clear_all(self) -> bool:
        """Clear all keys from Redis cache"""
        try:
            return bool(self._redis.flushall())
        except Exception as e:
            print(f"Redis clear error: {str(e)}")
            return False