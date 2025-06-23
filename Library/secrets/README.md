# SecretsManager

## Purpose

The SecretsManager handles secure, async secret management for the application:

- Retrieves and updates secrets via VaultManager
- Notifies listeners on secret changes
- Exposes metrics for all operations

## Features

- Async, thread-safe
- Vault integration
- Listener registration for secret change notifications
- API for get/set operations
- Prometheus metrics integration

## API

- `GET /secrets/{path}` – Retrieve a secret
- `PATCH /secrets/{path}` – Update or rotate a secret

## Metrics

- `secrets_manager_operations_total{operation="get"}`
- `secrets_manager_operations_total{operation="set"}`

## Usage

Instantiate with a VaultManager at app startup and inject into components as needed.
