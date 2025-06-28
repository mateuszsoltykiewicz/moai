# Vault Component

## Overview

Production-grade integration with HashiCorp Vault for secure secret management. Provides async operations, caching, and enhanced security. All API endpoints enforce JWT/OIDC authentication and RBAC authorization.

## Features

- **Secure Secret Storage**: Integrates with HashiCorp Vault
- **Async Operations**: Non-blocking secret read/write/delete
- **Caching**: In-memory TTL cache for secret retrieval
- **Token Management**: Automatic token renewal
- **Validation**: Enforces secret structure rules
- **Centralized Logging**: Uses `Library.logging` component
- **Prometheus Metrics**: Tracks Vault operations
- **JWT/OIDC Security**: All endpoints require authentication

## API Endpoints

| Endpoint               | Method | Description                  | Security (Required)  |
|------------------------|--------|------------------------------|----------------------|
| `/vault/secrets/{path}`| GET    | Retrieve secret by path      | JWT/OIDC, RBAC       |
| `/vault/secrets/{path}`| PUT    | Write secret by path         | JWT/OIDC, RBAC       |
| `/vault/secrets/{path}`| DELETE | Delete secret by path        | JWT/OIDC, RBAC       |
| `/vault/token/renew`   | POST   | Renew Vault token            | JWT/OIDC, RBAC       |

## Usage Example

Initialize VaultManager

vault_manager = VaultManager(
addr="https://vault.example.com",
token="s.xxxxx",
namespace="my-namespace"
)
await vault_manager.connect()
Read secret

secret, version = await vault_manager.read_secret("secret/data/myapp")
Write secret

version = await vault_manager.write_secret("secret/data/myapp", {"key": "value"})
Delete secret

await vault_manager.delete_secret("secret/data/myapp")
Renew token

token_info = await vault_manager.renew_token()

## Interactions

- **HashiCorp Vault**: Backend secret storage
- **Library.api.security**: JWT/OIDC validation and RBAC
- **Library.logging**: Centralized logging for all operations
- **Library.metrics**: Operation metrics collection

## Security

- All API endpoints enforce JWT/OIDC authentication and RBAC authorization
- Secrets are validated for structure and size
- Token renewal is handled automatically
- Sensitive data is never logged

## Potential Improvements

- Add support for Vault namespaces and multi-tenancy
- Implement secret version history and rollback
- Add integration with Vault audit logs

## Potential Bug Sources

1. **Vault Connectivity**: Network or auth failures
2. **Cache Invalidation**: Stale cache entries
3. **Permission Errors**: Insufficient Vault policies
4. **Validation Failures**: Invalid secret structures

## Logging

All operations use `Library.logging` with structured JSON format. Secret paths are logged, but secret values are never exposed.

## Last Updated

2025-06-28
