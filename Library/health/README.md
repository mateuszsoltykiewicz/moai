# HealthManager

## Purpose

The HealthManager provides centralized health status management for the application:

- Aggregates health status from all registered components
- Exposes liveness and readiness endpoints
- Integrates with metrics and logging

## Features

- Async, thread-safe
- Customizable health checks
- API for liveness and readiness probes
- Prometheus metrics integration

## API

- `GET /health/livez` – Liveness probe (always returns "alive" if service is running)
- `GET /health/readyz` – Readiness probe (returns aggregated health status)

## Usage

Instantiate at app startup and inject into components as needed.
Register health checks via `register_health_check()`.
