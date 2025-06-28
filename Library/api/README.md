# API Manager Component

## Overview

Central management system for FastAPI routers in the microservices architecture. Handles dynamic registration of API routes from various components with configuration-based enablement.

## Features

- **Dynamic Router Registration**: Automatically includes routers from enabled components
- **Configuration-Driven**: Enables/disables routers based on config settings
- **Async Lifecycle**: Supports setup and shutdown hooks
- **Metrics Integration**: Tracks router registration operations
- **Centralized Logging**: Uses `Library.logging` component

## Key Methods

- `setup(app: FastAPI, config)`: Registers all routers during application startup
- `register_router(router)`: Dynamically add new routers at runtime
- `list_routers()`: Get all registered routers
- `shutdown()`: Clean up resources during application shutdown

## Interactions

- **All Library Components**: Imports routers from each component's `api.py`
- **Library.config**: Uses configuration to determine enabled components
- **Library.metrics**: Records operations via Prometheus
- **Library.logging**: Centralized logging for all operations

## Potential Improvements

- Add health checks for router registration status
- Implement versioning support for API routes
- Add circuit breaker for dynamic router registration

## Potential Bug Sources

1. **Circular Imports**: Dynamic imports in `routers.py` could cause circular dependencies
2. **Configuration Errors**: Missing config values may disable required routers
3. **Thread Safety**: Dynamic router registration during runtime not thread-safe
4. **Compatibility**: FastAPI version upgrades may break router management

## Logging

All operations use `Library.logging` with structured JSON format and correlation IDs. Errors include full stack traces via `exc_info=True`.

## Usage Example

from fastapi import FastAPI
from Library.api.manager import ApiManager
app = FastAPI()
api_manager = ApiManager()
await api_manager.setup(app, config)