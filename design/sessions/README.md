# AppLib Sessions Module

## Overview

The `sessions` module provides robust, production-ready session and connection managers for all external resources used by the AppLib platform. Each session manager encapsulates the lifecycle, pooling, and cleanup of connections to databases, caches, message brokers, hardware buses, and external APIs. This approach ensures resource safety, testability, and seamless integration with both synchronous and asynchronous application components.

---

## Why Use Session Managers?

- **Resource Safety:** Ensures all connections are opened, pooled, and closed correctly, preventing leaks and contention.
- **Consistency:** Provides a unified interface for all adapters and services, regardless of backend type.
- **Testability:** Makes it easy to mock or substitute connections in unit/integration tests.
- **Observability:** Centralizes logging and error handling for all external resource access.
- **Extensibility:** New resource types can be added using the same proven patterns.

---

## Directory Structure

sessions/
├── init.py         # Unified registry for all session managers
├── database.py         # Async database session manager (SQLAlchemy/asyncpg)
├── redis.py            # Async Redis session manager (aioredis)
├── kafka.py            # Async Kafka producer/consumer manager (aiokafka)
├── i2c.py              # I2C hardware bus manager (smbus2/periphery)
├── canbus.py           # CAN bus manager (python-can)
├── http.py             # HTTP/External API session manager (httpx)


---

## Session Managers

| File         | Resource Type   | Key Features                                  |
|--------------|-----------------|-----------------------------------------------|
| database.py  | SQL/NoSQL DB    | Async, pooling, context manager, DI ready     |
| redis.py     | Cache/Session   | Async, pooling, context manager               |
| kafka.py     | Messaging       | Async, producer/consumer, context manager     |
| i2c.py       | Hardware Bus    | Sync/async, context manager                   |
| canbus.py    | CAN Bus         | Sync, context manager                         |
| http.py      | HTTP/API        | Async/sync, pooling, context manager          |
| __init__.py  | Registry        | Centralized access/config for all managers    |

---

## Usage Patterns

### 1. Centralized Registry

from sessions import SessionRegistry
registry = SessionRegistry(db_url=“postgresql+asyncpg://user:pass@db/app”,
                            redis_url=“redis://cache:6379/0”,
                            kafka_bootstrap_servers=“kafka:9092”,
                            kafka_group_id=“my-group”,
                            i2c_bus_id=1)
Database usage
async with registry.db as session:# Use session for DB operations
Redis usage
async with registry.redis as redis:
await redis.set(“foo”, “bar”)

### 2. Adapter Integration Example

from sessions.http import HTTPSessionManager
async def fetch_data():
  async with HTTPSessionManager(base_url=“https://api.example.com”) as client:
    response = await client.get(”/resource”)
    return response.json()


---

## Best Practices

- Use `with`/`async with` for all session managers to ensure safe resource handling.
- Configure session managers via your config system or environment variables.
- Integrate with your logging and error utilities for observability.
- Mock session managers in tests for fast, reliable CI/CD.
- Add new session managers as your platform evolves (e.g., S3, MQTT).

---

## Extending the Module

To add a new session manager:

1. Create a new file (e.g., `s3.py` or `mqtt.py`).
2. Implement a context-managed class for resource lifecycle.
3. Add it to `SessionRegistry` in `__init__.py`.
4. Update documentation and tests.

---

## References

- [SQLAlchemy Async ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [aioredis](https://aioredis.readthedocs.io/en/latest/)
- [aiokafka](https://aiokafka.readthedocs.io/en/stable/)
- [python-can](https://python-can.readthedocs.io/en/master/)
- [httpx](https://www.python-httpx.org/)
- [smbus2](https://pypi.org/project/smbus2/)

---

**The `sessions` module is your foundation for safe, efficient, and testable resource management across the AppLib platform.**
