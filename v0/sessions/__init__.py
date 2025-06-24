"""
Unified Session Registry for AppLib

- Centralizes access to all session managers (DB, Redis, Kafka, I2C, etc.).
- Supports dependency injection and testability.
- Loads configuration from a single config object or environment variables.
"""

from sessions.database import DatabaseSessionManager
from sessions.redis import RedisSessionManager
from sessions.kafka import KafkaSessionManager
from sessions.i2c import I2CBusManager

from typing import Optional
import os

class SessionRegistry:
    def __init__(
        self,
        db_url: Optional[str] = None,
        redis_url: Optional[str] = None,
        kafka_bootstrap_servers: Optional[str] = None,
        kafka_group_id: Optional[str] = None,
        i2c_bus_id: int = 1,
        # ...add more as needed
    ):
        # You can extend this to accept a config object (e.g., from Pydantic)
        self.db = DatabaseSessionManager(db_url or os.getenv("DB_URL", "sqlite+aiosqlite:///./test.db"))
        self.redis = RedisSessionManager(redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        self.kafka = KafkaSessionManager(
            bootstrap_servers=kafka_bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            group_id=kafka_group_id or os.getenv("KAFKA_GROUP_ID", "applib-group"),
        )
        self.i2c = I2CBusManager(bus_id=i2c_bus_id)

    # Optionally add helper methods for lifecycle management, e.g.:
    async def startup(self):
        # Eagerly establish connections if needed
        pass

    async def shutdown(self):
        # Gracefully close all connections if needed
        pass

# Usage example:
# registry = SessionRegistry(db_url="...", redis_url="...", ...)
# async with registry.db as session:
#     ...
