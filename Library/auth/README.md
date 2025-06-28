# Authentication & Authorization Component

## Overview

Centralized authentication and authorization service for microservices. Handles JWT validation and RBAC permission checks using Keycloak and Vault integration.

## Features

- **JWT Validation**: Verifies tokens using Keycloak's JWKS
- **RBAC Enforcement**: Checks permissions against policies stored in Vault
- **Centralized Logging**: Uses `Library.logging` for all operations
- **Type Safety**: Pydantic models for token claims and context

## Key Methods

- `validate_token(token: str) -> AuthContext`: Verifies JWT and extracts claims
- `check_permission(context: AuthContext, resource: str, action: str) -> bool`: Checks RBAC permissions

## Interactions

- **Keycloak**: Fetches JWKS for token validation
- **Library.secrets**: Retrieves RBAC policies from Vault
- **Library.logging**: Centralized logging for all operations
- **All Microservices**: Used as middleware for endpoint security

## Authentication Flow

sequenceDiagram
User->>Keycloak: Authenticate
Keycloak->>User: JWT
User->>Microservice: Request with JWT
Microservice->>AuthManager: validate_token(JWT)
AuthManager->>Keycloak: Fetch JWKS
AuthManager->>Microservice: AuthContext
Microservice->>AuthManager: check_permission(context, resource, action)
AuthManager->>Vault: Fetch RBAC policy
AuthManager->>Microservice: Permission status

## Potential Improvements

- Add token caching to reduce JWKS fetch frequency
- Implement token refresh mechanism
- Add support for custom claim validation

## Potential Bug Sources

1. **JWKS Fetch Failures**: Keycloak unavailability breaks authentication
2. **Clock Skew**: Token validation failures during time synchronization issues
3. **Policy Mismatches**: Vault policy format changes break RBAC checks
4. **Token Injection**: Lack of token binding allows token reuse

## Security Best Practices

- Always validate token signature and claims
- Use short-lived tokens with refresh mechanisms
- Store RBAC policies securely in Vault with versioning
- Regularly rotate Keycloak signing keys

## Logging

All operations use `Library.logging` with structured JSON format. Sensitive data (tokens, claims) is never logged.

## Usage Example

auth_manager = AuthManager(
keycloak_issuer="https://keycloak.example.com/realms/myrealm",
secrets_manager=secrets_manager,
rbac_policy_path="rbac/policies"
)