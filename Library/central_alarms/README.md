# Central Alarms Component

## Overview

Centralized alarm management system for aggregating and managing alarms from all microservices.  
**All API endpoints require JWT/OIDC authentication and authorization, supporting both human and machine-to-machine (M2M) scenarios using Keycloak and Vault.  
JWT/OIDC validation and RBAC are enforced via a reusable, generic dependency from `Library/api/security.py`.**

## Features

- **Centralized Alarm Management**: Single source of truth for all system alarms
- **Persistent Storage**: Integrates with `Library.database` for alarm persistence
- **JWT/OIDC Security**: All endpoints require valid Keycloak-issued JWTs, validated via Vault or directly against JWKS
- **RBAC Enforcement**: Role-based access control using claims from JWT and Vault policies
- **Metrics Integration**: Tracks operations and active alarm counts
- **Centralized Logging**: Uses `Library.logging` component

## API Endpoints

| Endpoint         | Method | Description                          | Security (Required)  |
|------------------|--------|--------------------------------------|----------------------|
| `/raise`         | POST   | Raise a new alarm                    | JWT/OIDC, RBAC       |
| `/clear`         | POST   | Clear an existing alarm              | JWT/OIDC, RBAC       |
| `/{alarm_id}`    | GET    | Get alarm by ID                      | JWT/OIDC, RBAC       |
| `/`              | GET    | List alarms (optionally active only) | JWT/OIDC, RBAC       |

## Security & Integration

- **Keycloak**: Issues JWTs for both users and services (M2M)
- **Vault**: Optionally validates JWTs, maps claims to policies/roles
- **Library.auth**: Handles JWT validation and RBAC checks in code
- **Library.api.security**: Provides reusable dependency for all API endpoints
- **No endpoint is accessible without a valid JWT**

## Usage Example

Example: Call from another service (M2M)

import requests
token = "<Keycloak-issued JWT>"
headers = {"Authorization": f"Bearer {token}"}
resp = requests.post(
"https://api.example.com/central_alarms/raise",
headers=headers,
json={"id": "foo", "source": "sensor", "type": "fault", "details": {}}
)


## Interactions

- **Library.database**: For persistent alarm storage
- **Library.auth**: For JWT validation and RBAC
- **Library.api.security**: For generic JWT/OIDC+RBAC enforcement
- **Library.logging**: Centralized logging for all operations
- **Library.metrics**: Operation and alarm count metrics

## Potential Improvements

- Add alarm deduplication to prevent duplicate entries
- Implement alarm expiration for stale alarms
- Integrate with notification systems (Slack, PagerDuty, etc.)

## Potential Bug Sources

1. **Token Validation**: If JWT validation fails, all API access will be denied
2. **Database Schema Mismatch**: Changes to alarm schema may break database operations
3. **Concurrency Issues**: High load may cause lock contention in registry

## Security Best Practices

- Rotate Keycloak signing keys and Vault secrets regularly
- Use HTTPS for all communications
- Audit alarm access and changes

## Logging

All operations use `Library.logging` with structured JSON format. Sensitive data (alarm details) is never logged.
