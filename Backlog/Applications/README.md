# Microservices Platform Overview

This document summarizes the key microservices in the platform, their responsibilities, and integration points.

## Microservices List and Responsibilities

| Microservice             | Core Responsibilities                                                                                                                      |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **ConfigurationServer**  | Centralized configuration provider with hot-reload, integrates with Vault, registry, state, exposes metrics, tracing, health, mTLS, RBAC.  |
| **ServiceRegistry**      | Tracks microservices and status, integrates with HomeKitBridge, manages alarms, exposes APIs with mTLS, RBAC, state, config, metrics, tracing, health. |
| **StateServer**          | Central state store for all services, exposes APIs with mTLS, RBAC, metrics, tracing, health.                                              |
| **SecretsRotator**       | Rotates secrets via Vault, checks dependencies, exposes APIs with mTLS, RBAC.                                                              |
| **AlarmsServer**         | Manages alarm lifecycle, history, triggers power cut-off on FATAL alarms, integrates with I2CAdapter and HomeKitBridge.                    |
| **BankManager**          | Handles sensor data, produces alarms, manages transactions, stops on FATAL alarms, integrates with AlarmsServer.                            |
| **CANBusAdapter**        | Integrates with Pi GPIO for CAN bus, produces sensor data and alarms, clears CANBus alarms on startup, stops on FATAL alarms.               |
| **DisasterDetector**     | Monitors FATAL alarms, detects disasters, produces DisasterDetected events, stops on FATAL alarms.                                          |
| **HeatingJob**           | Triggered by K8s/controller, manages heating cycles, raises/clears alarms, fails on temperature issues or FATAL alarms.                     |
| **HomeKitBridge**        | Integrates with StateRegistry for accessories, fetches config/schema, raises alarms if backend unreachable, exposes APIs with mTLS, RBAC.   |
| **HomeKitProtocolBridge**| Exposes platform accessories to Apple HomeKit via HAP, dynamically manages accessories, integrates via WebSocket with HomeKitBridge.        |
| **ExceptionsServer**     | Collects and stores exceptions from all microservices, raises security alarms for unauthorized services, attempts to fail unauthorized services. |
| **I2CAdapter**           | Controls relays via Raspberry Pi Pico, triggers power cut-off on FATAL alarms, exposes commands for power and heating control.              |
| **ServiceDiscovery**     | Discovers services via Kubernetes API/DNS, enforces allowed list from Vault, fails unauthorized services, updates ServiceRegistry.           |

## Integration and Common Components

All microservices integrate with the following common components and patterns:

- JWT/OIDC and RBAC for security enforcement
- mTLS for secure communication
- Vault for secrets management and configuration
- Prometheus metrics and OpenTelemetry tracing for observability
- Centralized logging and exception forwarding via Library components
- Service discovery and registry for dynamic endpoint resolution
- Async FastAPI with Uvicorn and asynccontextmanager lifespan for production-grade async services

## Directory Structure for Each Microservice

MyMicroservice/
├── main.py
├── api.py
├── manager.py
├── models.py
├── schemas.py
├── exceptions.py
├── metrics.py
├── config.py
├── README.md
├── init.py
├── requirements.txt
└── tests/
└── test_api.py

## Deployment and Best Practices

- Each microservice is independently deployable and versioned.
- Use Kubernetes for orchestration with health and readiness probes.
- Secure all communications with mTLS and enforce RBAC policies.
- Use Vault for centralized secrets and configuration management.
- Implement comprehensive logging, metrics, and tracing for observability.
- Follow fail-fast and circuit breaker patterns for resilience.
- Provide comprehensive README.md and tests for each microservice.

## Contact and Support

For questions or support, please contact the platform engineering team.
