# StateServer

## Overview

Centralized, production-grade state management service for all microservices.  
Implements async FastAPI server with Uvicorn, JWT/OIDC+RBAC, mTLS, metrics, tracing, and health endpoints.

## Features

- Async API for state get/set
- Persistent storage (DatabaseManager)
- Prometheus metrics and OpenTelemetry tracing
- JWT/OIDC + RBAC security
- mTLS support
- Health endpoints
- Exception forwarding

## API Endpoints

| Endpoint         | Method | Description         | Security (Required)  |
|------------------|--------|---------------------|----------------------|
| `/state/{key}`   | GET    | Get state by key    | JWT/OIDC, RBAC       |
| `/state/{key}`   | PUT    | Set state by key    | JWT/OIDC, RBAC       |

## Security

All endpoints require:

- mTLS client certificates
- Valid JWT with RBAC permissions
- `state:read` for GET endpoints
- `state:write` for PUT endpoints

## Health Checks

- `/health/live`: Liveness check
- `/health/ready`: Readiness check

## Metrics

- `state_server_operations_total`

## Logging

All operations use centralized structured logging via `Library.logging`.

## Last Updated

2025-06-28
