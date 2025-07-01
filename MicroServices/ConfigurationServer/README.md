# ConfigurationServer

## Overview

Centralized configuration service providing versioned, hot-reloadable configuration for all microservices. Implements production-grade async architecture with Uvicorn and FastAPI.

## Features

- Async API for config retrieval and hot-reload
- Config caching with Redis
- Integration with Vault for secrets
- Service registration/discovery
- JWT/OIDC + RBAC security
- Prometheus metrics, OpenTelemetry tracing
- Health endpoints
- Exception forwarding

## API Endpoints

| Endpoint                | Method | Description         | Security         |
|-------------------------|--------|---------------------|------------------|
| `/config/{service}`     | GET    | Get config          | `config:read`    |
| `/config/hot-reload`    | POST   | Reload config       | `config:write`   |

## Startup Sequence

1. Register with ServiceRegistry
2. Initialize Vault connection
3. Start API server
4. Load initial configuration

## Dependencies

- Vault (secrets storage)
- ServiceRegistry (service discovery)
- Redis (caching)

## Environment Variables

- `VAULT_ADDR`: Vault server URL
- `VAULT_TOKEN`: Vault authentication token
- `SERVICE_REGISTRY_URL`: ServiceRegistry endpoint

## Health Checks

- `/health/live`: Liveness check
- `/health/ready`: Readiness check

## Metrics

- `config_server_requests_total`
- `config_server_reload_total`

## Security

All endpoints require:

- mTLS client certificates
- Valid JWT with RBAC permissions
- `config:read` for GET endpoints
- `config:write` for POST endpoints

## Logging

All operations use centralized structured logging via `Library.logging`.

## Last Updated

2025-06-28
