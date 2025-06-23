# VaultManager

## Purpose

The VaultManager provides async, secure access to HashiCorp Vault for secret management:

- Read, write, and delete secrets
- Token renewal
- Error handling and observability

## Features

- Async, thread-safe
- Pydantic schema validation
- API for CRUD operations and token renewal
- Prometheus metrics integration

## API

- `GET /vault/secrets/{path}` – Retrieve a secret
- `PUT /vault/secrets/{path}` – Write a secret
- `DELETE /vault/secrets/{path}` – Delete a secret
- `POST /vault/token/renew` – Renew Vault token

## Metrics

- `vault_manager_operations_total{operation="read"}`
- `vault_manager_operations_total{operation="write"}`
- `vault_manager_operations_total{operation="delete"}`
- `vault_manager_operations_total{operation="renew"}`

## Usage

Instantiate with Vault address and token at app startup and inject into components as needed.
