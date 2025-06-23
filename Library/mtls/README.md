# MtlsManager

## Purpose

The MtlsManager provides centralized mTLS configuration and enforcement for the application:

- Manages mTLS certificate loading and validation
- Supports Kubernetes cert-manager integration (cert injection via volume)
- Optionally enforces mTLS for all or selected APIs

## Features

- Async, thread-safe
- API for diagnostics and enforcement
- Prometheus metrics integration

## API

- `GET /mtls/info` – Get current mTLS configuration and cert info
- `POST /mtls/enforce` – Dynamically enforce or relax mTLS (if allowed by policy)

## Usage

- Instantiate at app startup with config and inject into FastAPI/Uvicorn server.
- Use cert-manager in Kubernetes to inject certificates as volumes/secrets.
- Pass `ssl_context=mtls_manager.get_ssl_context()` to Uvicorn if enforcement is enabled.

## Kubernetes Integration

- Use cert-manager to manage and inject certificates as volumes.
- Reference the injected cert/key/CA paths in your config.
