# IoT Platform for Raspberry Pi Pico — Production-Grade MicroPython Suite

This repository provides a **comprehensive, production-grade IoT platform** for Raspberry Pi Pico W, built with MicroPython.  
It includes a robust, reusable IoT library and two reference device implementations: **SensorsController** and **RelaysController**.  
All components are designed for secure, event-driven, and observable integration with cloud-native and Kubernetes-based microservice architectures.

---

## Contents

- [`iotlib.py`](./iotlib.py): Reusable, modular IoT MicroPython library (network, security, config, state, logging, alarms, time sync, OTA, and more)
- [`sensors_controller.py`](./sensors_controller.py): Reference implementation for a secure, cloud-integrated sensor gateway
- [`relays_controller.py`](./relays_controller.py): Reference implementation for a secure, cloud-integrated relay/GPIO controller

---

## Features

- **WiFi connectivity management** with automatic reconnection
- **Secure device registration** with ServiceDiscovery
- **Dynamic configuration fetch & hot-reload** from ConfigurationServer
- **Watchdog heartbeat management** with auto-reset and state reporting
- **State synchronization** with StateServer (multi-tenancy/namespace support)
- **Structured JSON logging** with file rotation, masking, and retention
- **Alarm and exception reporting** with deduplication and buffering
- **NTP-based time synchronization** (configurable via ConfigurationServer)
- **OTA update hooks** for secure firmware upgrades
- **Role-based access control (RBAC)** and rate limiting for API endpoints
- **REST API for relay (GPIO) control** (RelaysController)
- **Passive WebSocket server for secure sensor streaming** (SensorsController)
- **Health and readiness endpoints** for orchestration and monitoring
- **Prometheus-compatible metrics**
- **Simulation mode for development and CI/CD**

---

## Components

### iotlib.py — IoT MicroPython Library

- **NetworkManager**: WiFi connection, reconnection, health monitoring
- **AuthManager**: Device key/JWT management, hot-reload, expiry, RBAC
- **ConfigManager**: Fetch, schema-validate, and hot-reload config
- **WatchdogManager**: Heartbeats, missed response tracking, auto-reset
- **StateManager**: State sync with StateServer, multi-tenancy support
- **Logger**: Structured JSON logging, rotation, retention, masking
- **TimeSyncManager**: Periodic NTP sync, drift/failure alerting
- **AlarmManager**: Alarm/exception buffering, deduplication, REST reporting
- **OTAUpdateManager**: Secure firmware update hooks
- **Health/Ready endpoints**: For orchestration/liveness checks

### SensorsController

- **Sensor data acquisition** and streaming (fields/configurable)
- **Passive WebSocket server** with token-based authentication and rate limiting
- **Secure registration, config, state, logging, alarms, time sync, OTA**
- **Hot-reloadable configuration and streaming logic**

### RelaysController

- **REST API for relay (GPIO) control** (`POST /gpio/<relay>`, `GET /gpio/<relay>`, `GET /gpio`)
- **Token-based authentication and RBAC for API**
- **Relay state management, atomic operations, and safe defaults**
- **Secure registration, config, state, logging, alarms, time sync, OTA**
- **Hot-reloadable relay configuration and logic**

---

## Usage Examples

### SensorsControlle

import uasyncio as asyncio
from sensors_controller import SensorsController
async def run():
controller = SensorsController(
wifi_ssid="<your_wifi_ssid>",
wifi_password="<your_wifi_password>",
device_id="<unique_device_id>",
device_key="<your_device_key>",
service_discovery_url="https://<service_discovery_host>/api/devices"
)
await controller.main()
asyncio.run(run())

### RelaysControlle

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
asyncio.run(run())

---

## Requirements

- MicroPython with uasyncio support
- Raspberry Pi Pico W or compatible hardware
- `iotlib.py` (included in this repository)
- `picoweb` or compatible MicroPython web framework for REST API (RelaysController)

---

## Extensibility

- Add domain-specific logic (sensors, relays, actuators, etc.)
- Extend with additional protocols (MQTT, WebSocket, etc.)
- Integrate with new microservices by reusing library components

---

## License

This project is proprietary to your organization.  
Please refer to your internal policies for use and distribution.

---
