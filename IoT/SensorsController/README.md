# SensorsController — Production-Grade MicroPython Application for Raspberry Pi Pico

This repository provides a **production-grade, event-driven, and secure implementation** of SensorsController for Raspberry Pi Pico W, using MicroPython and the reusable IoT library (`iotlib.py`).  
It is designed for robust operation in modern IoT and microservice environments.

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
- **Role-based access control (RBAC)** and rate limiting for API endpoints
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

---

## Usage Example

import uasyncio as asyncio
from iotlib import (
NetworkManager, AuthManager, ConfigManager, WatchdogManager, StateManager,
Logger, TimeSyncManager, AlarmManager, OTAUpdateManager
)
async def main():
network = NetworkManager("SSID", "PASSWORD")
auth = AuthManager("device_key")
config = ConfigManager("https://configserver/api", auth, "device_id")
watchdog = WatchdogManager("https://servicediscovery/api", auth, "device_id")
state = StateManager("https://stateserver/api", auth, "device_id")
logger = Logger(mask_fields=["token", "password"])
ntp = TimeSyncManager(["pool.ntp.org", "time.google.com"])
alarms = AlarmManager("https://alarms/api", auth, "device_id")
ota = OTAUpdateManager("https://updates/api", auth)
await network.connect()
asyncio.create_task(network.monitor())
asyncio.create_task(config.fetch_config_loop())
asyncio.create_task(watchdog.watchdog_loop())
asyncio.create_task(ntp.sync_loop())

### Use logger.log("INFO", "message") to log

### Use alarms.report_alarm({"type": "overtemp", "severity": "critical"}) to send alarms

asyncio.run(main())

---

## Extensibility

- Add domain-specific logic (e.g., GPIO/relay control, sensor streaming, REST endpoints).
- Extend with additional interfaces (MQTT, WebSocket, etc.).
- Integrate with new microservices by reusing library components.

---

## Requirements

- MicroPython with uasyncio support
- Raspberry Pi Pico W or compatible hardware
- `iotlib.py` (included in this repository)

---

## License

This project is proprietary to your organization.  
Please refer to your internal policies for use and distribution.

---
