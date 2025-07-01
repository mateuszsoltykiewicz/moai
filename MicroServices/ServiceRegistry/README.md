# ServiceRegistry

## Overview

Centralized, production-grade service registry for microservices discovery, health, and status.  
Implements async FastAPI server with Uvicorn, JWT/OIDC+RBAC, mTLS, metrics, tracing, and health endpoints.

## Features

- Async API for registration, heartbeat, deregistration, discovery
- In-memory registry (can be extended to persistent store)
- Prometheus metrics and OpenTelemetry tracing
- JWT/OIDC + RBAC security
- mTLS support
- Health endpoints
- Exception forwarding

## API Endpoints

| Endpoint                         | Method | Description                         | Security (Required)  |
|-----------------------------------|--------|-------------------------------------|----------------------|
| `/registry/register`              | POST   | Register a service instance         | JWT/OIDC, RBAC       |
| `/registry/heartbeat`             | POST   | Heartbeat for a service instance    | JWT/OIDC, RBAC       |
| `/registry/deregister`            | POST   | Deregister a service instance       | JWT/OIDC, RBAC       |
| `/registry/services`              | GET    | List all healthy service instances  | JWT/OIDC, RBAC       |
| `/registry/instance/{svc}/{id}`   | GET    | Get a specific service instance     | JWT/OIDC, RBAC       |

## Security

All endpoints require:

- mTLS client certificates
- Valid JWT with RBAC permissions
- `registry:read` for GET endpoints
- `registry:write` for POST endpoints

## Health Checks

- `/health/live`: Liveness check
- `/health/ready`: Readiness check

## Metrics

- `service_registry_operations_total`
- `service_registry_registered_instances`

## Logging

All operations use centralized structured logging via `Library.logging`.

## Last Updated

2025-06-28
