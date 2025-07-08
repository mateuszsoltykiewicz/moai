# Schemas Component

## Overview

Centralized schema registry for managing and serving Pydantic schemas across microservices.  
**All schemas must be registered at startup via dependency injection.**  
**All API endpoints require JWT/OIDC authentication and RBAC authorization.**

## Features

- **Schema Registration**: Inject schemas at startup via `register_schema()`
- **Schema Discovery**: List and retrieve schemas by name
- **Versioning Support**: Use naming conventions like `UserProfile:v1`
- **Centralized Logging**: Uses `Library.logging` component
- **Prometheus Metrics**: Tracks schema operations
- **JWT/OIDC Security**: All endpoints require authentication

## Usage

### 1. Schema Registration (Microservice Startup)

from Library.schemas import SchemasManager
from myapp.schemas import UserSchema, ProductSchema # Your Pydantic models
Initialize during app startup

schemas_manager = SchemasManager()
schemas_manager.register_schema("UserProfile:v1", UserSchema)
schemas_manager.register_schema("Product:v2", ProductSchema)

### 2. API Integration

from Library.schemas import create_router
Create and include router

schemas_router = create_router(schemas_manager)
app.include_router(schemas_router)

## API Endpoints

| Endpoint          | Method | Description                     | Security (Required)  |
|-------------------|--------|---------------------------------|----------------------|
| `/schemas/`       | GET    | List all registered schema names| JWT/OIDC, RBAC       |
| `/schemas/{name}` | GET    | Get schema definition by name   | JWT/OIDC, RBAC       |

## Key Components

| Component         | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `SchemasManager`  | Core schema registration and retrieval logic                            |
| `create_router()` | Factory function to create FastAPI router with security                 |
| `register_schema` | Method to inject schemas at startup                                    |

## Constraints

- **Mandatory Registration**: All schemas must be registered via `register_schema()` at startup
- **No Hardcoding**: Schemas must not be hardcoded in business logic
- **Registry as Source of Truth**: The registry is the sole source for schema definitions

## Interactions

- **All Microservices**: Register schemas at startup and retrieve via API
- **Library.api.security**: For JWT/OIDC validation and RBAC
- **Library.logging**: Centralized logging for all operations
- **Library.metrics**: Operation metrics collection

## Potential Improvements

- Add schema validation endpoints
- Implement schema diffing between versions
- Add automatic documentation generation

## Security Best Practices

- Restrict schema registration to authorized services
- Validate all schema names to prevent injection
- Rotate JWT signing keys regularly

## Logging

All operations use `Library.logging` with structured JSON format.  
Schema names are logged, but sensitive schema content is omitted.

## Last Updated

2025-06-28
