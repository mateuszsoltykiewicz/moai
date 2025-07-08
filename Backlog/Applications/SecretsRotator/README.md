# SecretsRotator

## Overview

Centralized, production-grade secrets rotation service for all microservices.  
Implements async FastAPI server with Uvicorn, JWT/OIDC+RBAC, mTLS, metrics, tracing, and health endpoints.

## Features

- Async API for secret rotation
- Integration with Vault for secrets management
- Dependency checks for Vault and database
- Prometheus metrics and OpenTelemetry tracing
- JWT/OIDC + RBAC security
- mTLS support
- Health endpoints
- Exception forwarding

## API Endpoints

| Endpoint         | Method | Description         | Security (Required)  |
|------------------|--------|---------------------|----------------------|
| `/secrets/rotate`| POST   | Rotate secret       | JWT/OIDC, RBAC       |

## Security

All endpoints require:

- mTLS client certificates
- Valid JWT with RBAC permissions
- `secrets:write` for POST endpoints

## Health Checks

- `/health/live`: Liveness check
- `/health/ready`: Readiness check

## Metrics

- `secrets_rotator_operations_total`

## Logging

All operations use centralized structured logging via `Library.logging`.

## Last Updated

2025-06-28
