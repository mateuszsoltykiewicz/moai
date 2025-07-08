# Central State Component

## Overview

Centralized service registry for tracking microservice health, versions, and endpoints. Implements automatic health status detection and provides a unified view of all services.

## Features

- **Service Registration**: Services register/update their state
- **Health Monitoring**: Automatic stale/offline detection
- **Endpoint Discovery**: Unified view of all service endpoints
- **JWT/OIDC Security**: All endpoints require valid Keycloak-issued JWTs
- **Metrics Integration**: Tracks operations and service counts

## API Endpoints

| Endpoint         | Method | Description                          | Security (Required)  |
|------------------|--------|--------------------------------------|----------------------|
| `/register`      | POST   | Register/update service state        | JWT/OIDC, RBAC       |
| `/services`      | GET    | List all services with status        | JWT/OIDC, RBAC       |
| `/service/{name}`| GET    | Get service by name                  | JWT/OIDC, RBAC       |

## Key Components

| File              | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `manager.py`      | Core service state management and health monitoring                     |
| `api.py`          | FastAPI endpoints with JWT/OIDC security                               |
| `schemas.py`      | Pydantic models for service state                                      |
| `metrics.py`      | Prometheus metrics for operations and service counts                   |

## Security & Integration

- **JWT/OIDC Validation**: Uses `Library/api/security` dependency
- **RBAC Enforcement**: Requires `central_state:write` for registration and `central_state:read` for queries
- **Database Integration**: Stores service state via `Library.database`

## Usage Example

Service registration

state = ServiceState(
name="payment-service",
version="1.2.3",
endpoints={"process": "http://payments/process"},
last_heartbeat=datetime.utcnow()
)
await central_state_registry.register_or_update(state)
Query services

services = await central_state_registry.list_services()


## Potential Improvements

- Add service deregistration endpoint
- Implement automatic garbage collection for stale services
- Add webhook notifications for status changes

## Potential Bug Sources

1. **Clock Skew**: Time differences may cause incorrect health status
2. **Concurrency**: High registration rates may cause lock contention
3. **Schema Changes**: Database schema must match ServiceState model
4. **Heartbeat Frequency**: Incorrect timeout values may mark healthy services as stale

## Logging

All operations use `Library.logging` with structured JSON format. Service names and versions are logged, but sensitive endpoint details are omitted.
