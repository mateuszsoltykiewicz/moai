# Secrets Management Component

## Overview

Secure secrets management system with version control, caching, and change notifications.  
**All API endpoints require JWT/OIDC authentication and RBAC authorization.**

## Features

- **Secure Storage**: Integrates with Vault for secret storage
- **Version Control**: Supports CAS (Check-And-Set) for atomic updates
- **Caching**: Local cache for frequently accessed secrets
- **Change Notifications**: Listeners for real-time secret updates
- **Validation**: Enforces secret structure rules
- **Centralized Logging**: Uses `Library.logging` component
- **Prometheus Metrics**: Tracks all secret operations

## API Endpoints

| Endpoint                | Method | Description                      | Security (Required)  |
|-------------------------|--------|----------------------------------|----------------------|
| `GET /secrets/{path}`   | GET    | Retrieve secret by path          | JWT/OIDC, RBAC       |
| `PATCH /secrets/{path}` | PATCH  | Update secret with CAS version   | JWT/OIDC, RBAC       |

## Key Components

| Component         | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `SecretsManager`  | Core secret operations with caching and validation                      |
| `api.py`          | FastAPI endpoints with security enforcement                             |
| `schemas.py`      | Pydantic models for requests/responses                                 |
| `metrics.py`      | Prometheus metrics for operations                                      |

## Security

- **JWT/OIDC Validation**: Uses `Library/api/security` dependency
- **RBAC Enforcement**: Requires `secrets:read` for retrieval and `secrets:write` for updates
- **Vault Integration**: All secrets are stored in HashiCorp Vault
- **No Plaintext Secrets**: Secrets are never logged or exposed in responses

## Usage Example

Get secret

secret = await secrets_manager.get("database/password")
Update secret

await secrets_manager.set(
"api/keys",
{"key": "new-secret-key"},
version=current_version
)
Add listener

def secret_changed(path: str, value: dict):
print(f"Secret {path} changed")
secrets_manager.add_listener("my_service", secret_changed)

## Potential Improvements

- Add secret rotation automation
- Implement historical version retrieval
- Add approval workflows for sensitive updates

## Potential Bug Sources

1. **Cache Invalidation**: Stale cache may return old secrets
2. **Version Conflicts**: Concurrent updates may cause version conflicts
3. **Permission Errors**: Incorrect RBAC may block legitimate access
4. **Validation Gaps**: Weak validation may allow insecure secrets

## Security Best Practices

- Rotate secrets regularly
- Use short-lived JWTs for access
- Restrict secret paths with RBAC
- Audit all secret access and changes

## Logging

All operations use `Library.logging` with structured JSON format.  
Secret paths are logged, but secret values are never exposed in logs.

## Last Updated

2025-06-28
