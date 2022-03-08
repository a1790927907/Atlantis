import aioredis
from typing import Optional


class RedisClient:
    def __init__(self, redis_url: str, **kwargs):
        self.redis_url = redis_url
        self.kwargs = kwargs
        self.redis_client: Optional[aioredis.Redis] = None

    async def connect(self):
        if self.redis_client is None:
            self.redis_client = await aioredis.from_url(self.redis_url, **self.kwargs)
        return self.redis_client

    @property
    def is_connected(self) -> bool:
        return bool(self.redis_client)

    def reset_connection(self):
        self.redis_client = None
