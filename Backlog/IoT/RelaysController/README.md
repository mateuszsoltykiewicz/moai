# RelaysController — Production-Grade MicroPython Application for Raspberry Pi Pico

**RelaysController** is a robust, secure, and event-driven microservice for controlling relays (GPIO outputs) on Raspberry Pi Pico W using MicroPython.  
It is designed for seamless integration with Kubernetes-native platforms and leverages a reusable IoT library (`iotlib.py`) for all core connectivity, security, configuration, logging, and monitoring needs.

---

## Features

- **WiFi connectivity management** with automatic reconnection
- **Secure device registration** with ServiceDiscovery
- **Dynamic configuration fetch & hot-reload** from ConfigurationServer
- **Watchdog heartbeat management** with auto-reset and state reporting
- **State synchronization** with StateServer
- **Structured JSON logging** with file rotation, masking, and retention
- **Alarm and exception reporting** with deduplication and buffering
- **NTP-based time synchronization** (configurable via ConfigurationServer)
- **OTA update hooks** for secure firmware upgrades
- **Role-based access control (RBAC)** and rate limiting for REST API endpoints
- **REST API for relay (GPIO) control** (`POST /gpio/<relay>`, `GET /gpio/<relay>`, `GET /gpio`)
- **Health and readiness endpoints** for orchestration and monitoring
- **Prometheus-compatible metrics**
- **Multi-tenancy and namespace support**
- **Simulation mode for development and CI/CD**

---

## Main Components

### NetworkManager

Handles WiFi connection, reconnection, and network health monitoring.

### AuthManager

Manages device keys and JWT tokens, supports hot-reload, expiry checks, and RBAC.

### ConfigManager

Fetches configuration from ConfigurationServer, supports schema validation, hot-reload, and fallback.

### WatchdogManager

Sends periodic watchdog heartbeats, tracks missed responses, triggers device reset.

### StateManager

Synchronizes device state with StateServer, supports tenant/namespace IDs.

### Logger

Structured JSON logger with file rotation, retention, masking, and audit trail support.

### TimeSyncManager

Periodically synchronizes device time with NTP servers from configuration.

### AlarmManager

Buffers, deduplicates, and reports alarms/exceptions to central servers.

### OTAUpdateManager

Hooks for secure OTA firmware update, validation, and rollback.

### RelayGPIOManager

Manages relay (GPIO) state, safety, and provides atomic relay operations.

---

## Usage Example

import uasyncio as asyncio
from relays_controller import RelaysController
async def run():
relay_pins = {"relay1": 2, "relay2": 3} # Example: GPIO2 and GPIO3
controller = RelaysController(
wifi_ssid="<your_wifi_ssid>",
wifi_password="<your_wifi_password>",
device_id="<unique_device_id>",
device_key="<your_device_key>",
service_discovery_url="https://<service_discovery_host>/api/devices",
relay_pins=relay_pins
)
await controller.main()
To run on your device, uncomment:

asyncio.run(run())

---

## REST API Endpoints

- `POST /gpio/<relay>` — Set relay state (`{"state": "HIGH"}` or `{"state": "LOW"}`), requires valid JWT and RBAC.
- `GET /gpio/<relay>` — Get current state of specified relay.
- `GET /gpio` — Get current state of all relays.

---

## Extensibility

- Add domain-specific logic (timers, schedules, feedback, diagnostics).
- Extend with additional interfaces (MQTT, WebSocket, etc.).
- Integrate with new microservices by reusing library components.

---

## Requirements

- MicroPython with uasyncio support
- Raspberry Pi Pico W or compatible hardware
- `iotlib.py` (included in this repository)
- `picoweb` or compatible MicroPython web framework for REST API

---

## License

This project is proprietary to your organization.  
Please refer to your internal policies for use and distribution.

---
