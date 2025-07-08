# Service Registry Component

## Overview

Centralized service registry for microservice discovery and health monitoring.  
**All API endpoints require JWT/OIDC authentication and RBAC authorization.**

## Features

- **Service Registration**: Services register with host, port, and metadata
- **Heartbeat Monitoring**: Tracks service health with periodic heartbeats
- **Automatic Cleanup**: Removes expired service instances
- **Service Discovery**: Query service instances by name
- **Prometheus Metrics**: Tracks operations and instance counts
- **Centralized Logging**: Uses `Library.logging` component

## API Endpoints

| Endpoint                   | Method | Description                         | Security (Required)  |
|----------------------------|--------|-------------------------------------|----------------------|
| `/registry/register`       | POST   | Register a service instance         | JWT/OIDC, RBAC       |
| `/registry/heartbeat`      | POST   | Update service heartbeat            | JWT/OIDC, RBAC       |
| `/registry/deregister`     | POST   | Deregister a service instance       | JWT/OIDC, RBAC       |
| `/registry/services`       | GET    | List all services and instances     | JWT/OIDC, RBAC       |
| `/registry/instance/{...}` | GET    | Get service instance by ID          | JWT/OIDC, RBAC       |

## Key Components

| File          | Purpose                                                                 |
|---------------|-------------------------------------------------------------------------|
| `manager.py`  | Core registry logic with health monitoring and cleanup                  |
| `api.py`      | FastAPI endpoints with security enforcement                             |
| `schemas.py`  | Pydantic models for requests and responses                              |
| `metrics.py`  | Prometheus metrics for operations and instance counts                   |

## Usage Example

Service registration

await registry_manager.register(RegisterRequest(
service_name="payment-service",
instance_id="pay-001",
host="10.0.0.5",
port=8080
))
Periodic heartbeat

await registry_manager.heartbeat(HeartbeatRequest(
service_name="payment-service",
instance_id="pay-001"
))
Service discovery

services = await registry_manager.list_services()

## Interactions

- **All Microservices**: Register, heartbeat, and deregister
- **Library.api.security**: For JWT/OIDC validation and RBAC
- **Library.logging**: Centralized logging for all operations
- **Library.metrics**: Operation and instance count metrics

## Potential Improvements

- Add persistent storage for service registry state
- Implement watch mechanism for service changes
- Add health check endpoints for service instances

## Potential Bug Sources

1. **Clock Drift**: Time differences may cause premature instance cleanup
2. **Concurrency**: High registration rates may cause lock contention
3. **Network Partitions**: May cause false positive instance removals
4. **Memory Pressure**: Large number of instances may cause OOM errors

## Security Best Practices

- Rotate JWT signing keys regularly
- Restrict deregister permissions to service owners
- Monitor instance count metrics for anomalies

## Logging

All operations use `Library.logging` with structured JSON format. Service names and instance IDs are logged, but sensitive metadata is omitted.

## Last Updated

2025-06-28
