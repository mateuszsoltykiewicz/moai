# Admission Component

## Overview

Implements a Kubernetes Validating Admission Webhook for enforcing custom pod admission policies, including service allowlisting, registration checks, and pod security policies.

## Features

- **mTLS and RBAC-based authentication/authorization** for webhook requests
- **Service allowlist** and **ServiceRegistry** integration for dynamic policy enforcement
- **Pod security checks** (e.g., privileged container denial)
- **Centralized logging** via `Library.logging`
- **Async, non-blocking** operations throughout

## API Endpoints

| Endpoint         | Method | Description                  |
|------------------|--------|------------------------------|
| `/validate`      | POST   | AdmissionReview validation   |

## Interactions

- **Library.auth**: AuthManager for RBAC/authorization
- **Library.mtls**: MtlsManager for mTLS authentication
- **Library.registry**: ServiceRegistryManager for service registration validation
- **Library.config**: ConfigManager for allowlist retrieval
- **Library.logging**: All logging operations

## Potential Improvements

- Add Prometheus metrics for webhook calls, denials, and latencies
- Add more granular policy configuration (e.g., namespace-based rules)
- Add richer error responses for easier debugging

## Potential Bug Sources

- Type mismatches if the incoming AdmissionReview does not conform to expected schema
- Blocking calls if any integrated manager is not truly async
- Missing logging if centralized logger is not configured correctly

## Logging

All logs are handled through `Library.logging` with structured, contextual output for audit and debugging.

## Usage Example

Example: Validate a pod admission request (internal use)

response = await admission_manager.validate_pod(admission_request)
if not response.response.allowed:
# Deny pod creation