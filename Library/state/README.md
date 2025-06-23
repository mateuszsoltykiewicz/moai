# StateManager

## Purpose

The StateManager provides centralized, async state management for the application.

- Stores and retrieves state for all components
- Supports partial updates and deletion
- Integrates with sessions for stateful resources
- Notifies listeners of state changes
- Exposes metrics for all operations

## Features

- Async, thread-safe
- Pydantic schema validation
- Listener registration for state change notifications
- API for CRUD operations
- Prometheus metrics integration

## API

- `GET /state/{key}` – Get state for a key
- `PUT /state/{key}` – Set or update state for a key
- `DELETE /state/{key}` – Delete state for a key
- `GET /state/` – Get all state

## Metrics

- `state_manager_operations_total{operation="get"}`
- `state_manager_operations_total{operation="set"}`
- `state_manager_operations_total{operation="update"}`
- `state_manager_operations_total{operation="delete"}`
- `state_manager_operations_total{operation="get_all"}`

## Usage

Instantiate at app startup and inject into components as needed.
