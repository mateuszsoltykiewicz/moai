# Database Component

## Overview

Production-grade, config-driven database manager for PostgreSQL with dynamic table creation and CRUD operations. Supports JWT/OIDC authentication and RBAC authorization for all operations.

## Features

- **Dynamic Table Creation**: Tables defined in configuration
- **Async CRUD Operations**: Thread-safe async operations
- **Config-Driven Schema**: Table schemas defined in app config
- **Centralized Logging**: Uses `Library.logging` component
- **Prometheus Metrics**: Tracks all database operations
- **JWT/OIDC Security**: All endpoints require authentication

## API Endpoints

| Endpoint                  | Method | Description                  | Required Permission |
|---------------------------|--------|------------------------------|---------------------|
| `POST /database/{table}`  | POST   | Create record                | `database:write`   |
| `GET /database/{table}/{id}` | GET  | Get record by ID            | `database:read`    |
| `GET /database/{table}`   | GET    | List records with limit     | `database:read`    |
| `PUT /database/{table}/{id}` | PUT  | Update record by ID         | `database:write`   |
| `DELETE /database/{table}/{id}` | DELETE | Delete record by ID      | `database:delete`  |

## Key Components

| File          | Purpose                                                                 |
|---------------|-------------------------------------------------------------------------|
| `manager.py`  | Core database operations and dynamic ORM management                     |
| `api.py`      | FastAPI endpoints with security enforcement                            |
| `schemas.py`  | Pydantic models for requests/responses                                 |
| `metrics.py`  | Prometheus metrics for database operations                             |
| `exceptions.py` | Custom database exceptions                                            |

## Interactions

- **Library.config**: For table schema definitions
- **Library.api.security**: For JWT/OIDC+RBAC enforcement
- **Library.logging**: Centralized logging for all operations
- **Library.metrics**: Operation metrics collection

## Potential Improvements

- Add support for database migrations
- Implement connection pooling metrics
- Add query batching for bulk operations

## Potential Bug Sources

1. **Schema Mismatches**: Configuration must match database schema
2. **Connection Leaks**: Ensure proper connection management
3. **Lock Contention**: High concurrency may cause performance issues
4. **Error Handling**: Transaction rollbacks must be reliable

## Security Best Practices

- Validate all input data against schemas
- Use parameterized queries to prevent SQL injection
- Restrict database permissions to minimum required
- Encrypt sensitive data at rest and in transit

## Logging

All operations use `Library.logging` with structured JSON format. Sensitive data is never logged.

## Usage Example

Initialize

db_manager = DatabaseManager("postgresql+asyncpg://user:pass@host/db", config_manager)
await db_manager.setup()
Create record

await db_manager.create_record("users", {"id": "user1", "name": "Alice"})
Query records

users = await db_manager.query_records("users", limit=10)