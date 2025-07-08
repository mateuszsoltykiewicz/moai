# Redis Component

## Overview

Production-grade Redis integration providing async access to key-value storage, hashes, pub/sub, streams, and distributed locks. Fully integrated with centralized security and logging.

## Features

- **Async Redis Client**: Non-blocking operations using redis-py
- **Data Structures**: Key-value, hashes, streams
- **Pub/Sub**: Real-time messaging support
- **Distributed Locks**: Coordination across services
- **Health Checks**: Connection monitoring
- **Centralized Logging**: Uses `Library.logging` component
- **Prometheus Metrics**: Tracks all operations
- **JWT/OIDC Security**: All API endpoints require authentication

## API Endpoints

| Endpoint       | Method | Description                  | Security (Required)  |
|----------------|--------|------------------------------|----------------------|
| `/redis/status`| GET    | Redis health status          | JWT/OIDC, RBAC       |
| `/redis/kv`    | GET    | Get key-value by key         | JWT/OIDC, RBAC       |
| `/redis/kv`    | POST   | Set key-value with expiration| JWT/OIDC, RBAC       |

## Key Methods

- `get/set/delete`: Basic key-value operations
- `hgetall/hset`: Hash operations
- `publish/subscribe`: Pub/sub messaging
- `acquire_lock/release_lock`: Distributed locking
- `xadd/xread`: Stream operations
- `health_check`: Connection health

## Interactions

- **Redis Server**: Backend data store
- **Library.api.security**: JWT/OIDC+RBAC enforcement
- **Library.logging**: Centralized logging
- **Library.metrics**: Operation metrics

## Security

- All endpoints enforce JWT/OIDC authentication and RBAC
- Requires `redis:read` for GET operations and `redis:write` for mutations
- No unauthenticated access

## Usage Example

redis_manager = RedisManager(redis_url="redis://localhost")
await redis_manager.setup()
Set value

await redis_manager.set("user:1", "Alice", expire=3600)
Get value

user = await redis_manager.get("user:1")
Publish message

await redis_manager.publish("alerts", "System started")

## Potential Improvements

- Add connection pooling metrics
- Implement automatic retry for failed operations
- Add stream consumer groups support

## Potential Bug Sources

1. **Redis Server Unavailability**: Network issues or Redis downtime
2. **Lock Leaks**: Improper lock release causing deadlocks
3. **Memory Pressure**: Large values causing Redis OOM errors
4. **Configuration Mismatch**: Incorrect SSL or password settings

## Logging

All operations use structured JSON logging via `Library.logging`. Errors include full stack traces.

## Last Updated

2025-06-28
