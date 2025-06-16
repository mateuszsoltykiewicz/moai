# AppLib

A modular, async-first, production-grade Python platform for hardware, messaging, and cloud-native microservices.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Features](#features)
- [Quickstart](#quickstart)
- [Configuration & Hot Reload](#configuration--hot-reload)
- [Security](#security)
- [Observability](#observability)
- [Deployment & Scalability](#deployment--scalability)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**AppLib** is a highly modular, async Python platform built on FastAPI.  
It provides robust adapters for hardware (CANBus, I2C), messaging (Kafka), security (mTLS, Vault), and cloud-native operations (metrics, tracing, logging, updates).  
The architecture is designed for extensibility, observability, and production reliability.

---

## Architecture

### High-Level Flow

- **Entry Point:** Uvicorn/ASGI server receives HTTP(S) requests and passes them to FastAPI.
- **Routing Layer:** `api/routers/` contains all REST endpoints, grouped by domain. Routers use dependency injection for authentication, adapters, and config/state access.
- **Adapters/Services Layer:** `adapters/` abstract external systems (Kafka, Vault, mTLS, tracing, etc.). `subservices/` implement business logic, orchestrating adapters as needed.
- **Data & State:** `models/` and `schemas/` define Pydantic models for API, internal logic, config, and state. `core/config.py` manages async, hot-reloadable config. `core/state.py` manages encrypted, versioned app state.
- **Sessions:** `sessions/` manages async connections to databases, brokers, and other persistent resources.
- **Metrics, Logging, Tracing:** `metrics/` defines Prometheus metrics. `core/logging.py` and `core/tracing.py` provide structured logging and distributed tracing.
- **Response:** Data is validated/serialized via Pydantic and returned to the client. Errors are handled by custom exception handlers.

### Configuration & Hot Reload Features

- `core/config.py` (AsyncConfigManager) loads and validates config from JSON, applies env overrides, and supports hot reload with async listeners.
- Updates are orchestrated via the update adapter, which uses ConfigService and AppState for atomic, validated, and observable hot reloads.

### Security Features

- Authentication (JWT, OAuth2) via FastAPI dependencies.
- Sensitive operations require authorization.
- mTLS is enforced at the ingress/proxy level, with endpoints to check mTLS status and health.

### Observability Features

- **Metrics:** All business, adapter, and API events are counted and measured in `metrics/`.
- **Tracing:** All requests and async operations are traced (OpenTelemetry), with context propagated across services.
- **Logging:** Structured, JSON logs are sent to Fluentd or other log aggregators, with dynamic log level control.

### Deployment & Scalability

- **Docker/Kubernetes:** Containerized with Helm charts for deployment and scaling.
- **CI/CD:** Automated pipelines for build, test, and deploy.
- **Microservice-ready:** Each subservice/module can be refactored into a standalone microservice if needed.

---

## Project Structure

---

## Features

- **Async-first:** All I/O and external calls are async for maximum concurrency.
- **Adapters:** Modular adapters for CANBus, I2C, Kafka, Vault, mTLS, tracing, and more.
- **Config & State:** Hot-reloadable, validated config and encrypted, versioned app state.
- **Observability:** Built-in metrics, tracing, and logging for full operational insight.
- **Security:** JWT/OAuth2 authentication, mTLS support, and RBAC-ready endpoints.
- **Extensibility:** Add new adapters, routers, or services with minimal friction.
- **Production-ready:** Designed for Docker, Kubernetes, and CI/CD.

---

## Quickstart

Install dependencies
pip install -r requirements.txt
Run development server
uvicorn api.main:app –reload
Run tests
pytest

---

## Configuration & Hot Reload

- Edit config files in `configs/` (per environment).
- Supports environment variable overrides and hot reload via `core/config.py`.
- Update endpoints and adapters use ConfigService and AppState for atomic, validated updates.

---

## Security

- Authentication via JWT/OAuth2.
- mTLS enforced at ingress/proxy, with status endpoints for verification.
- Secrets managed via Vault integration.

---

## Observability

- Prometheus metrics exposed at `/metrics`.
- Distributed tracing via OpenTelemetry (Jaeger, Tempo, etc.).
- Structured logging with Fluentd integration.

---

## Deployment & Scalability

- Kubernetes-ready (see `charts/`).
- CI/CD pipelines for automated build, test, and deploy.
- Modular design allows horizontal scaling and microservice extraction.

---

## Contributing

1. Fork the repo and create your feature branch.
2. Write clear, tested code and update docs as needed.
3. Submit a pull request and describe your changes.

---

## License

[MIT](LICENSE)

---

## Deep Dive: Architecture Flow

See [Architecture](#architecture) above for a detailed breakdown of request flow, configuration, state management, and observability.

---

**For diagrams, advanced usage, or troubleshooting, see the `docs/` or ask the maintainers!**
