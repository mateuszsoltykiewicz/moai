# State Management Component

## Overview

Production-grade state management system with persistence, caching, and distributed synchronization.  
**All API endpoints require JWT/OIDC authentication and RBAC authorization.**

## Features

- **State Persistence**: Stores state in database with Redis caching
- **Distributed Locking**: Redis-based locks for concurrent access
- **Change Notifications**: Event bus integration for state changes
- **Partial Updates**: Merge updates into existing state
- **Size Validation**: 1MB state value limit
- **Centralized Logging**: Uses `Library.logging` component
- **Prometheus Metrics**: Tracks all state operations

## API Endpoints

| Endpoint       | Method | Description                  | Security (Required)  |
|----------------|--------|------------------------------|----------------------|
| `GET /state/{key}` | GET  | Get state by key            | JWT/OIDC, RBAC       |
| `PUT /state/{key}` | PUT  | Set/update state by key     | JWT/OIDC, RBAC       |

## Key Components

| Component         | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `StateManager`    | Core state operations with caching and locking                          |
| `api.py`          | FastAPI endpoints with security enforcement                             |
| `schemas.py`      | Pydantic models for requests/responses                                 |
| `metrics.py`      | Prometheus metrics for operations                                      |

## Security

- **JWT/OIDC Validation**: Uses `Library/api/security` dependency
- **RBAC Enforcement**: Requires `state:read` for GET and `state:write` for PUT
- **No Unauthenticated Access**: All endpoints require valid JWT

## Usage Example

Set state

await state_manager.set("user:123", {"preferences": {"theme": "dark"}})
Get state

state = await state_manager.get("user:123")
Partial update

await state_manager.update("user:123", {"preferences": {"font_size": 14}})
Delete state

await state_manager.delete("user:123")

## Interactions

- **Library.database**: For state persistence
- **Library.redis**: For caching and locking
- **Library.events**: For state change notifications
- **Library.api.security**: JWT/OIDC validation and RBAC
- **Library.logging**: Centralized logging for all operations
- **Library.metrics**: Operation metrics collection

## Potential Improvements

- Add state versioning and history
- Implement state TTL/expiration
- Add watch API for state changes
- Implement state change approvals

## Potential Bug Sources

1. **Cache Invalidation**: Stale cache may return old state
2. **Lock Contention**: High concurrency may cause performance issues
3. **Event Ordering**: Out-of-order state change events
4. **Schema Drift**: State structure changes may break consumers

## Security Best Practices

- Encrypt sensitive state values
- Rotate JWT signing keys regularly
- Restrict state paths with RBAC
- Audit all state access

## Logging

All operations use `Library.logging` with structured JSON format.  
State keys are logged, but values are never exposed in logs.

## Last Updated

2025-06-28
