# ExceptionsServer

## Overview

Centralized exception management service for all microservices. Stores exceptions, enforces allowed service list, and raises security alarms for unauthorized services.

## Features

- Stores all exceptions in a database (exception_name, service, status, last_change)
- Fetches allowed service list from Vault
- Raises security alarms and attempts to fail unauthorized microservices
- Exposes REST API for managing and querying exceptions
- Integrates with Library.exceptions for exception forwarding
- Metrics, tracing, and health endpoints

## API Endpoints

| Endpoint                    | Method | Description                     | Security         |
|-----------------------------|--------|---------------------------------|------------------|
| `/exceptions/`              | POST   | Create a new exception          | JWT/OIDC, RBAC   |
| `/exceptions/`              | GET    | List/query exceptions           | JWT/OIDC, RBAC   |
| `/exceptions/allowed-services` | GET | List allowed services           | JWT/OIDC, RBAC   |

## Security

- JWT/OIDC + RBAC for all endpoints
- mTLS for internal communication
- Vault for secrets and allowed service list

## Health Checks

- `/health/live`
- `/health/ready`

## Metrics

- `exceptions_total` (Prometheus)

## Last Updated

2025-07-01
