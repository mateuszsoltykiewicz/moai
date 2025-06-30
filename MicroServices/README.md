# IoT Microservices Platform for Heater Control (Raspberry Pi CM5)

## Overview

This platform implements a **mission-critical, event-driven IoT control system** for a single-site water heater, built on Kubernetes with Strimzi Kafka, Vault, and Prometheus.  
It features robust safety mechanisms, mTLS security, HomeKit integration, and comprehensive observability.  
**If a FATAL alarm occurs, the system will cut power to the heater and require manual intervention for recovery.**

---

## Architecture Principles

- **Event-driven:** Kafka is the backbone for all inter-service communication.
- **Single-site, safety-first:** Controls one heater (Raspberry Pi CM5), not a distributed cloud system.
- **Observability:** All alarms, health, and metrics are visible in HomeKit and Prometheus/Grafana.
- **Security:** mTLS (with cert-manager) and API authentication are enforced for all API-enabled pods.
- **Manual disaster recovery:** No auto-restart after FATAL; operator reviews alarms in HomeKit and restarts manually.

---

## Core Microservices & Responsibilities

### AlarmsServer

- Owns and creates `createAlarm` and `deleteAlarm` Kafka topics (via Helm/Strimzi).
- Consumes from both topics; does not produce to them.
- Adds alarms to registry and DB on `createAlarm`, marks as inactive (never deletes) on `deleteAlarm`.
- Maintains full alarm history (soft-delete only).
- Creates tables if not present.
- Keeps operational state in StateServer.
- Fetches config from ConfigurationServer at startup and on hot-reload.
- Exposes Prometheus metrics, OpenTelemetry tracing, health endpoints.
- Supports secrets rotation via Vault.
- APIs protected by mTLS (cert-manager injected) and authentication.
- Acts as backend for HAP accessory, reporting current alarms to HomeKit/iPhone.
- **Triggers power circuit cut-off relay via I2CAdapter if FATAL alarm is detected.**

### BankManager

- Consumes from `sensorData`.
- Produces to `createAlarm` and `deleteAlarm` as needed.
- Creates/uses its own tables if not present.
- On FATAL alarm (from AlarmsServer or local logic), **crashes and stops processing**.
- APIs protected by mTLS and authentication.
- Fetches config from ConfigurationServer with hot-reload.
- Integrates with AlarmsServer API for alarm status.
- Full metrics, telemetry, health, secrets support.

### CANBusAdapter

- Integrates with Raspberry Pi CM5 GPIO for CAN bus.
- Owns and creates `sensorData` topic.
- Produces sensor data, and can produce `createAlarm` or `deleteAlarm` based on CAN bus status.
- Creates/uses its own tables if not present.
- On FATAL alarm, **crashes and stops processing**.
- Clears all CANBus-specific alarms on startup.
- APIs protected by mTLS and authentication.
- Fetches config from ConfigurationServer with hot-reload.
- Integrates with AlarmsServer API for alarm status.
- Full metrics, telemetry, health, secrets support.

### ConfigurationServer

- Provides configuration to all services; supports hot-reload and rollout.
- Fails to start if no configuration is provided (bootstrap via ConfigMap).
- Produces to `createAlarm` and `deleteAlarm` as needed.
- Creates/uses its own tables if not present.
- On FATAL alarm, **crashes and stops processing**.
- Clears all configuration-specific alarms on startup.
- APIs protected by mTLS and authentication.
- Full state, secrets, health, metrics, telemetry support.

### DisasterDetector

- Monitors FATAL alarms from AlarmsServer (API or Kafka).
- Only monitors water temperature if a HeatingJob is running.
- Produces to `DisasterDetected` topic when disaster is detected.
- Owns and creates `DisasterDetected` topic.
- Consumes from `sensorData` (with filter).
- Creates/uses its own tables if not present.
- On FATAL alarm, **crashes and stops processing**.  
  **Will not be restarted by Kubernetes until platform is manually restarted.**
- APIs protected by mTLS and authentication.
- Fetches config from ConfigurationServer with hot-reload.
- Integrates with AlarmsServer API for alarm status.
- Full metrics, telemetry, health, secrets support.
- Clears all disaster-specific alarms on startup.

### HeatingJob

- Triggered by Kubernetes API or controller (e.g., custom JobController).
- Produces to `I2CHeating` topic.
- Consumes from `sensorData` (with filter).
- Creates/uses its own tables if not present.
- Raises heating alarm when triggered, deletes when finished.
- Fails with exit code 1 and raises alarm if temperature change is not detected within configured period.
- On FATAL alarm, **fails immediately**.
- Clears all heating job-specific alarms on startup.
- APIs protected by mTLS and authentication.
- Fetches config from ConfigurationServer with hot-reload.
- Integrates with AlarmsServer API for alarm status.
- Full metrics, telemetry, health, secrets, state support.

### HomeKitBridge

- Integrates with StateRegistry to add/remove accessories.
- Fetches configuration and accessory schema from ConfigurationServer or Library.
- Raises alarm if any backend is not reachable via StateRegistry.
- APIs protected by mTLS and authentication.

### I2CAdapter

- Controls relays (gas valve, spark, power cut-off) via Raspberry Pi Pico.
- **On FATAL alarm (from AlarmsServer), triggers power cut-off relay to physically disconnect heater power.**
- Clears all I2C adapter-specific alarms on startup.
- On FATAL alarm, **fails and stops processing**.
- Produces to `createAlarm` and `deleteAlarm` as needed.
- APIs protected by mTLS and authentication.
- Fetches config from ConfigurationServer with hot-reload.
- Integrates with AlarmsServer API for alarm status.
- Full metrics, telemetry, health, secrets, state support.

### SecretsRotator

- Rotates secrets for all services via Vault.
- Checks that Vault and database are deployed before operating.
- Fails if any critical dependency is missing.
- APIs protected by mTLS and authentication.

### StateRegistry

- Tracks all deployed microservices and their status.
- Integrates with HomeKitBridge for accessory configuration.
- Discovers services via Kubernetes DNS or API.
- FATAL alarm if unauthorized service is detected.
- Clears registry alarms on startup; deletes alarm if service becomes discoverable again.
- Can stop watching specific services via API.
- Acts as cluster status registry.
- Backs up state to database; creates tables if not present.
- APIs protected by mTLS and authentication.

### ExceptionsServer

- Collects exceptions occurred across kubernetes microservices
- Store it's state in StateServer
- Works with ServiceRegistry and ServiceDiscovery
- Fetches configuration from ConfigurationServer
- Communicates with HomeKitBridge, acts as an accessory to provide exceptions count

---

## Safety & Disaster Handling

- **Power Circuit Cut-Off:**  
  On FATAL alarm, I2CAdapter triggers a dedicated relay to physically cut power to the heater. This is a mandatory safety feature and must be tested during commissioning.
- **No Automated Disaster Recovery:**  
  If a FATAL event occurs, the system will not auto-restart. HomeKit/iPhone app will show the alarm and status. Only manual intervention (platform restart) can clear a FATAL disaster state.
- **Startup Self-Check:**  
  All services must clear their own service-specific alarms on startup and create database tables if not present.
- **Crash on FATAL:**  
  All services must crash and stop operating on FATAL alarm.

---

## Security

- **mTLS Everywhere:**  
  All pods exposing APIs run with mTLS enabled. Certificates are injected via cert-manager.
- **API Authentication:**  
  All APIs that require authentication enforce it (JWT, API key, or OAuth2, as appropriate).
- **Vault Integration:**  
  All secrets are managed and rotated via Vault.

---

## Observability

- **Metrics:**  
  All services expose Prometheus metrics.
- **Tracing:**  
  All services support OpenTelemetry tracing.
- **Health:**  
  All services expose health endpoints.
- **Alarms:**  
  All alarms are visible in HomeKit and via API.

---

## Communication Matrix

| Topic               | Producers                  | Consumers                 |
|---------------------|---------------------------|---------------------------|
| `createAlarm`       | All services               | AlarmsServer              |
| `deleteAlarm`       | All services               | AlarmsServer              |
| `sensorData`        | CANBusAdapter              | BankManager, HeatingJob   |
| `DisasterDetected`  | DisasterDetector           | StateRegistry             |
| `I2CHeating`        | HeatingJob                 | I2CAdapter                |

---

## Deployment & Startup

1. **Deploy foundational services first:**  
   - ConfigurationServer  
   - SecretsRotator  
   - StateRegistry  
   - AlarmsServer  
2. **Deploy hardware adapters and business logic services next.**
3. **All services must validate configuration and dependencies at startup.**
4. **All services must clear their own alarms on startup.**

---

## Additional Notes

- **Retention & Archival:**  
  Alarms are never physically deleted from the database; status is updated to inactive. Consider retention/archival policies for long-term storage.
- **Hardware Watchdog:**  
  For maximum safety, implement a hardware watchdog on the Raspberry Pi Pico to ensure relays return to a safe state on software failure.
- **HomeKit Integration:**  
  HomeKitBridge and AlarmsServer ensure that all critical statuses and alarms are visible to the operator’s iPhone.

---

## License

[Your License Here]

---

**This platform is designed for safety, reliability, and operational transparency.  
If a disaster occurs, the system will halt and await operator review and restart.  
All alarms and statuses are visible in HomeKit and via API for maximum clarity and control.**
