# Adapters

Adapters are the integration layer between AppLib and external systems, protocols, or hardware.  
They encapsulate all low-level details, provide async interfaces, and enable testability, observability, and abstraction for the rest of the platform.

---

## Purpose

- **Abstraction:** Hide the complexity of external APIs, hardware, protocols, or cloud services from business logic and API routers.
- **Async-first:** All adapters are designed for async use with FastAPI and asyncio.
- **Observability:** Adapters emit metrics, logs, and traces for all major operations and errors.
- **Testability:** Adapters are easy to mock, inject, and test in isolation.
- **Security:** Sensitive operations (e.g., mTLS, Vault, secrets) are handled securely and never leak secrets to logs.

---

## Supported Adapters

### 1. CANBus Adapter (`canbus.py`)
- **Purpose:**  
  Provides an abstraction layer for CAN bus hardware integration, enabling async communication with CAN devices using the SocketCAN interface.
- **Key Features:**  
  - Async read and write operations for CAN messages.
  - Health checks and automatic reconnection logic for robust operation.
  - Protocol-specific decoding/encoding support for various CAN message formats.
  - Metrics and structured logging for observability.
  - Fully compatible with Raspberry Pi Compute Module 5 when using standard SPI-based CAN controllers (e.g., MCP2515).
- **Usage:**  
  Used for interfacing with industrial devices, automotive equipment, or any hardware communicating over CAN bus.

### 2. I2C Adapter (`i2c.py`)
- **Purpose:**  
  Abstracts I2C hardware communication, allowing async command execution and device management over I2C channels.
- **Key Features:**  
  - Async command queueing and execution for I2C transactions.
  - GPIO configuration and management for devices supporting additional pin modes.
  - Health monitoring with automatic reconnection to maintain device availability.
  - Protocol abstraction for custom encoding/decoding of I2C messages.
  - Metrics for command execution, errors, and health status.
  - Supports up to four I2C channels on Raspberry Pi Compute Module 5 via GPIO.
- **Usage:**  
  Ideal for sensor integration, hardware monitoring, and embedded device control.

### 3. mTLS Adapter (`mtls.py`)
- **Purpose:**  
  Manages mutual TLS (mTLS) certificates and SSL context for secure communication between services.
- **Key Features:**  
  - Loads certificates from cert-manager-managed Kubernetes secrets or Vault.
  - Hot-reloads certificates on rotation and exposes health/status checks.
  - Integrates with your configuration manager for dynamic path updates.
  - Provides SSL context for both client and server-side mTLS.
  - Emits metrics for certificate expiration, reloads, and errors.
- **Usage:**  
  Ensures encrypted, authenticated connections for internal and external service communication.

### 4. Tracing Adapter (`tracing.py`)
- **Purpose:**  
  Provides distributed tracing integration using OpenTelemetry or similar frameworks.
- **Key Features:**  
  - Async context manager for span creation and management.
  - Exposes trace context and current trace IDs for correlation.
  - Integrates with Prometheus metrics for span counts, errors, and durations.
  - Works seamlessly with FastAPI and async code.
- **Usage:**  
  Enables end-to-end observability and performance analysis across all services and adapters.

### 5. Updates Adapter (`updates.py`)
- **Purpose:**  
  Orchestrates application updates, including config and state hot-reloads, with rollback and validation.
- **Key Features:**  
  - Checks for available updates from a remote server or repository.
  - Performs atomic update operations with state backup and rollback on failure.
  - Integrates with the config manager and app state for safe, validated updates.
  - Emits metrics for update attempts, completions, failures, and durations.
- **Usage:**  
  Supports zero-downtime updates and configuration changes in production environments.

### 6. Vault Adapter (`vault.py`)
- **Purpose:**  
  Integrates with HashiCorp Vault to securely manage secrets, credentials, and dynamic/static database credentials.
- **Key Features:**  
  - Async secret retrieval, storage, and deletion.
  - Supports dynamic database credentials with lease management and renewal.
  - Implements static credential rotation and root credential rotation.
  - Caching with TTL for frequently accessed secrets.
  - Multiple authentication methods (token, AppRole, Kubernetes).
  - Metrics for secret operations, latency, and errors.
- **Usage:**  
  Centralizes secret management, credential rotation, and secure configuration for all services.

---

## Summary Table

| Adapter         | Purpose                                        | Key Features                                              | Pi CM5 Support |
|-----------------|------------------------------------------------|-----------------------------------------------------------|----------------|
| canbus.py       | CAN bus hardware abstraction                   | Async read/write, health, protocol, metrics               | Yes            |
| i2c.py          | I2C hardware abstraction                       | Async commands, GPIO config, health, metrics              | Yes            |
| mtls.py         | mTLS certificate/SSL context management        | Cert-manager/Vault, hot reload, health, metrics           | N/A            |
| tracing.py      | Distributed tracing (OpenTelemetry, etc.)      | Async spans, context, metrics                             | N/A            |
| updates.py      | Application update orchestration               | Async update, rollback, config/state integration, metrics | N/A            |
| vault.py        | HashiCorp Vault secrets/credentials management | Async secrets, DB creds rotation, cache, metrics          | N/A            |

---

## Raspberry Pi Compute Module 5 Support

Adapters for CANBus and I2C are fully compatible with Raspberry Pi Compute Module 5:

- **CANBus:** Use MCP2515 or compatible HAT via SPI and SocketCAN; works with `python-can`.
- **I2C:** Supports up to 4 external I2C channels via GPIO; works with `smbus`, `smbus2`, or async I2C libraries.
- **Same configuration and code patterns as other Raspberry Pi models.**

---

## Usage Example



Adapters are typically injected into subservices or routers via dependency injection or factory functions.

---

## Design Principles

- **Single Responsibility:** Each adapter handles one external system or protocol.
- **Async Everywhere:** All I/O is non-blocking and compatible with FastAPI async endpoints.
- **Metrics & Observability:** All adapters emit Prometheus metrics and structured logs.
- **Error Handling:** All exceptions are wrapped in custom error types and logged with context.
- **Extensibility:** Adapters can be extended or swapped (e.g., for different hardware or cloud providers).
- **Security:** Never log secrets or sensitive data. Use secure patterns for credentials and certificates.

---

## Testing

- All adapters should have unit and integration tests with mocks/fakes for external systems.
- Use dependency injection to swap real adapters with test doubles in your tests.

---

## Metrics & Observability

- Adapters increment Prometheus counters and histograms for key operations (success, error, latency).
- All operations are logged with context using the platform logger.
- Tracing adapters propagate trace context for distributed observability.

---

## Adding a New Adapter

1. Create a new file in `adapters/` (e.g., `kafka.py`, `redis.py`, `s3.py`, `homekit.py`).
2. Implement an async class with a clear, minimal interface.
3. Integrate metrics, logging, error handling, and tracing.
4. Add unit tests and update this README.

---

## Security Best Practices

- Never log secrets, tokens, or passwords.
- Use secure storage (Vault, Kubernetes secrets) for all credentials.
- Validate and sanitize all external data.
- Use proper SSL/TLS context for all network connections.

---

## References

- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [HashiCorp Vault Python Client (hvac)](https://hvac.readthedocs.io/en/stable/)
- [cert-manager for Kubernetes](https://cert-manager.io/docs/)
- [HAP-python for HomeKit](https://github.com/ikalchev/HAP-python)
- [Raspberry Pi Compute Module 5 Docs](https://www.raspberrypi.com/documentation/computers/compute.html)

---

**For questions or to propose a new adapter, open an issue or contact the maintainers.**
