# ServiceDiscovery

## Overview

ServiceDiscovery dynamically discovers running microservices in the Kubernetes cluster, enforces an allow-list fetched from Vault, and raises alarms for unauthorized services.

## Features

- Kubernetes API-based service discovery
- Vault-managed allowed service list
- Raises FATAL alarms for unauthorized services
- Attempts to terminate unauthorized services
- Updates ServiceRegistry with healthy services
- JWT/OIDC + RBAC + mTLS security
- Prometheus metrics and tracing
- Health endpoints

## API Endpoints

| Endpoint           | Method | Description                  | Security         |
|--------------------|--------|------------------------------|------------------|
| `/discovery/services` | GET    | List discovered services     | JWT/OIDC, RBAC   |
| `/discovery/allowed`  | GET    | List allowed services        | JWT/OIDC, RBAC   |

## Deployment

- Requires Kubernetes API access
- Vault for allowed services secret
- ServiceRegistry integration

## Metrics

- `service_discovery_runs_total`
- `unauthorized_service_detections_total`

## Health Checks

- `/health/live`
- `/health/ready`

## Last Updated

2025-07-01
