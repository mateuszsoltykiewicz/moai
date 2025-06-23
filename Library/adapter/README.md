# AdapterManager

## Purpose

The AdapterManager provides centralized, async adapter management for the application:

- Manages registration, retrieval, and lifecycle of hardware/software adapters
- Supports dynamic adapter loading based on configuration
- Integrates with sessions, metrics, and logging

## Features

- Async, thread-safe
- API for adapter creation, registration, and discovery
- Prometheus metrics integration

## API

- `POST /adapter/` – Create or retrieve an adapter instance by type and config
- `GET /adapter/` – List all registered adapter types

## Usage

Instantiate at app startup and inject into components as needed.
Register new adapter classes via `register_adapter()`.
