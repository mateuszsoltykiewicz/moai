# ApiManager

## Purpose

The ApiManager provides centralized API router and lifecycle management for the application:

- Registers and manages all FastAPI routers
- Supports dynamic router registration and dependency injection
- Integrates with OpenAPI docs, metrics, and logging

## Features

- Async, thread-safe
- API for router registration and status
- Prometheus metrics integration

## Usage

Instantiate at app startup and call `setup(app)` with your FastAPI app instance.
Routers are registered from `api/routers.py`.
