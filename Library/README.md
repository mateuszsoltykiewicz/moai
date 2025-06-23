# Library

## Overview

**Library** is a modular, async, production-grade Python platform for modern IoT, industrial, and cloud-native applications.  
It provides a robust foundation for device, protocol, and data management, supporting microservices, event-driven architectures, and seamless integration with Kubernetes and cloud platforms.

---

## Architecture

- **Config-driven:** All features and components are enabled/disabled via configuration.
- **Async:** All managers and APIs are fully async for maximum scalability.
- **Extensible:** Add new components or adapters with minimal changes.
- **Observability:** Metrics, tracing, health, and alarms are first-class citizens.
- **Security:** mTLS, Vault, and RBAC ready.
- **Kubernetes-native:** Supports cert-manager, config injection, and cloud-native operations.

---

## Components

### Mandatory Components

| Component          | Directory    | Purpose/Key Features                                                                 |
|--------------------|-------------|-------------------------------------------------------------------------------------|
| **CoreManager**      | `core/`      | Orchestration, base logic, lifecycle hooks                                         |
| **ConfigManager**    | `config/`    | Async config loading, hot reload, schema validation, env overrides                 |
| **StateManager**     | `state/`     | Central state store, session registry, persistence                                 |
| **SecretsManager**   | `secrets/`   | Secret lifecycle, Vault integration, rotation, audit                               |
| **VaultManager**     | `vault/`     | HashiCorp Vault client, token management, secret versioning                        |
| **MetricsManager**   | `metrics/`   | Prometheus/OpenMetrics, custom metrics, aggregation                                |
| **TracingManager**   | `tracing/`   | OpenTelemetry tracing, distributed context, test spans                             |
| **HealthManager**    | `health/`    | Liveness/readiness, dependency graph, aggregated health                            |
| **AlarmsManager**    | `alarms/`    | Alarm/event storage, escalation, notification, audit                               |
| **SessionsManager**  | `sessions/`  | Session lifecycle, pooling, resource management                                    |
| **UtilsManager**     | `utils/`     | Logging, utilities, helpers                                                        |
| **SchemasManager**   | `schemas/`   | Pydantic schemas, registry, validation                                             |
| **ApiManager**       | `api/`       | API router registry, OpenAPI docs, dynamic router registration                     |
| **AdapterManager**   | `adapter/`   | Adapter registry, dynamic loading, connection handling                             |

### Optional Components

| Component        | Directory    | Purpose/Key Features                                                                 |
|------------------|-------------|-------------------------------------------------------------------------------------|
| **KafkaManager**     | `kafka/`     | Async Kafka producer/consumer, event streaming, topic management                   |
| **I2CManager**       | `i2c/`       | I2C hardware, GPIO relay/valve/pump control, Pi CM5/Pico support                   |
| **CanbusManager**    | `canbus/`    | CANBus sensor streaming, config, event streaming                                   |
| **DatabaseManager**  | `database/`  | Async PostgreSQL, dynamic multi-table support, state/event persistence             |
| **MtlsManager**      | `mtls/`      | mTLS enforcement, cert-manager integration, Kubernetes native                      |
| **HAPManager**       | `hap/`       | HomeKit Accessory Protocol, Apple ecosystem integration                            |

---

## Directory Structure

Library/
├── core/
├── config/
├── state/
├── secrets/
├── vault/
├── metrics/
├── tracing/
├── health/
├── alarms/
├── sessions/
├── utils/
├── schemas/
├── api/
├── adapter/
├── kafka/        # Optional
├── i2c/          # Optional
├── canbus/       # Optional
├── database/     # Optional
├── mtls/         # Optional
├── hap/          # Optional
└── README.md

---

## Integration Philosophy

- **Component Enablement:**  
  All optional components are enabled/disabled via configuration (`config/manager.py`).  
  Only enabled components are loaded, registered, and exposed via API.

- **API Management:**  
  All APIs are registered via `ApiManager` and are modular.  
  Optional APIs are included only if their component is enabled.

- **Adapters & Sessions:**  
  Adapters interact with Sessions for connection pooling and resource management.  
  StateManager and DatabaseManager can persist session and state data.

- **Security:**  
  mTLS (via MtlsManager) and Vault-based secrets are supported out-of-the-box.  
  Cert-manager integration is ready for Kubernetes-native deployments.

- **Observability:**  
  Metrics, tracing, health, and alarms are available for all components.  
  Prometheus, OpenTelemetry, and health endpoints are standard.

---

## Usage

1. **Configure** your application in `config/` (enable/disable components, set paths, etc.).
2. **Start** your application. Only enabled components will be loaded.
3. **Interact** via the API endpoints (see each component's README for details).
4. **Monitor** via `/metrics`, `/health/livez`, `/health/readyz`, `/alarms/`, and tracing endpoints.

---

## Adding a New Component

1. Create a new directory (e.g., `myfeature/`).
2. Implement `manager.py`, `schemas.py`, `api.py`, etc.
3. Add your router to `api/routers.py` (conditionally, if optional).
4. Document your component with a `README.md`.
5. Add config options and register with `ConfigManager` and `ApiManager`.

---

## Example: Enabling Optional Components

{
  “enabled_components”: {
    “kafka”: true,
    “i2c”: true,
    “canbus”: false,
    “database”: true,
    “mtls”: true,
    “hap”: false
  }
}

---

## Observability & Security

- **Metrics:** `/metrics`
- **Tracing:** `/tracing/test-span`, `/tracing/info`
- **Health:** `/health/livez`, `/health/readyz`
- **Alarms:** `/alarms/`
- **mTLS:** `/mtls/info`, `/mtls/enforce`
- **Secrets:** Vault integration, `/secrets/`

---

## Contributing

- Each component is documented and tested in isolation.
- Follow the naming conventions and async best practices.
- PRs must include a `README.md` in the component directory.

---

## License

[Your License Here]

---

This platform is designed for real-world, scalable, and secure deployments.  
For details, see each component’s README. For architecture questions or contributions, open an issue or PR!
