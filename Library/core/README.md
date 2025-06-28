# Core Component

## Overview

Central orchestrator for core logic and service coordination.  
**All API endpoints require JWT/OIDC authentication and RBAC authorization via the generic dependency from `Library/api/security.py`.**

## Features

- **Centralized Orchestration**: Coordinates core services and managers
- **Async Lifecycle**: Supports async setup and shutdown
- **Health/Status Reporting**: Exposes `/core/status` endpoint
- **JWT/OIDC Security**: All endpoints require valid Keycloak-issued JWTs
- **RBAC Enforcement**: Role-based access control using claims from JWT and Vault policies
- **Metrics Integration**: Tracks core operations
- **Centralized Logging**: Uses `Library.logging` component

## API Endpoints

| Endpoint      | Method | Description               | Security (Required)  |
|---------------|--------|---------------------------|----------------------|
| `/core/status`| GET    | Get core status/health    | JWT/OIDC, RBAC       |

## Security & Integration

- **JWT/OIDC Validation**: Uses `Library/api/security` dependency
- **RBAC Enforcement**: Requires `core:read` for status endpoint
- **Centralized Logging**: All logs via `Library.logging`

## Usage Example

from fastapi import FastAPI
from Library.core.api import router as core_router
app = FastAPI()
app.include_router(core_router)


## Potential Improvements

- Add more granular health checks for subcomponents
- Expose metrics endpoint for Prometheus scraping

## Potential Bug Sources

1. **Improper Initialization**: If `setup()` is not called, state may be incomplete
2. **Concurrency**: Async state changes must be thread-safe if expanded
3. **Security**: Missing JWT or RBAC enforcement will expose sensitive status

## Logging

All operations use `Library.logging` with structured JSON format.
