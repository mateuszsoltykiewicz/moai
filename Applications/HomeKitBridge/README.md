# HomeKitBridge

## Overview

HomeKitBridge integrates your platform with Apple HomeKit, making alarms and accessories available to iOS devices. It manages HomeKit accessories, synchronizes with StateRegistry, and raises alarms if backends are unreachable.

## Features

- Lists and refreshes HomeKit accessories via API
- Integrates with StateRegistry for accessory management
- Fetches configuration and schemas from ConfigurationServer
- Raises alarms if any backend is unreachable
- Exposes metrics, tracing, health, secrets, and state endpoints
- APIs protected by mTLS and JWT/OIDC with RBAC

## API Endpoints

| Endpoint                | Method | Description                  | Security (Required)  |
|-------------------------|--------|------------------------------|----------------------|
| `/homekit/accessories`  | GET    | List HomeKit accessories     | JWT/OIDC, RBAC       |
| `/homekit/refresh`      | POST   | Refresh accessory list       | JWT/OIDC, RBAC       |

## Security

All endpoints require:

- mTLS client certificates
- Valid JWT with RBAC permissions
- `homekit:read` for GET endpoints
- `homekit:write` for POST endpoints

## Health Checks

- `/health/live`: Liveness
- `/health/ready`: Readiness

## Metrics

- `homekit_refreshes_total`

## Logging

All operations use centralized structured logging via `Library.logging`.

## Last Updated

2025-06-28
