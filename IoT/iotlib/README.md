# IoT/iotlib — Comprehensive README

`iotlib` is a **production-grade, reusable MicroPython library** for building robust, async-driven IoT solutions on platforms such as Raspberry Pi Pico W. It provides foundational building blocks for device configuration, state management, disaster detection, watchdog monitoring, and network control, and is designed for easy extension and integration with custom device controllers.

---

## Features

- **Centralized Configuration**: Shared state, disaster flags, and API registration in a single object.
- **Async Task Utilities**: Helpers for robust, cancellable asyncio task management.
- **Disaster Handling**: Detects and manages disaster conditions, coordinates safe shutdown.
- **Watchdog Monitoring**: Heartbeat endpoint and missed-heartbeat detection.
- **Network Management**: WiFi connection and network health monitoring.
- **REST API Registration**: Dynamic, self-validating API setup.
- **Hardware Agnostic**: No direct pin assignments; extend for any IoT device.
- **Extensible**: Designed for subclassing and integration in application modules.

---

## Directory Structure

mateuszsoltykiewicz@MacBook-Pro-2 iotlib % tree
.
├── README.md
├── __init__.py
├── configuration.py
├── disaster.py
├── network.py
├── shutdown.py
└── watchdog.py

1 directory, 7 files

---

## Module Overview

### 1. `config.py`

**Purpose**: Provides the base `Configuration` and `RelaysConfiguration` classes for managing system state, disaster flags, hardware references, and REST API registration.

#### `Configuration`

- Centralizes all system state and disaster flags.
- Handles API registration and readiness validation.
- Provides a REST endpoint for configuration inspection.

**Key Attributes:**
- `disaster_detected`, `disaster_reason`, `should_shutdown`, `shutdown_ready`, `exit_code`
- `api_ready`, `registered_apis`, `_required_apis`
- `wlan`, `connection_timeout`

**Key Methods:**
- `_apis_setup()`: Registers REST endpoints.
- `get_configuration(request)`: Returns current config as JSON.
- `validate_apis()`: Checks all required APIs are registered.

#### `RelaysConfiguration`

- Extends `Configuration` for relay-based devices.
- Adds hardware pin references and sensor/metric attributes.
- Designed for heating, water, or similar control systems.

**Additional Attributes:**
- Hardware: `pump`, `gas_valve`, `spark`
- Metrics: `current_temperature`, `metrics_poll_url`, `metrics_last_update`, `water_available`, `gas_leak`, etc.

---

### 2. `async_utils.py`

**Purpose**: Utility functions for managing asyncio tasks.

**Key Function:**
- `cancel_all(tasks)`: Cancels and awaits a list of asyncio tasks, handling `CancelledError`.

---

### 3. `disaster.py`

**Purpose**: Disaster detection and shutdown coordination.

#### `DisasterController`

- Monitors `disaster_detected` flag in configuration.
- Triggers safe shutdown and logs reasons.
- Waits for shutdown readiness and raises if not completed.

**Usage Example:**

from IoT.iotlib.disaster import DisasterController
disaster = DisasterController(config)
asyncio.create_task(disaster.disaster_monitor())

---

### 4. `watchdog.py`

**Purpose**: Heartbeat endpoint and missed-heartbeat detection.

#### `WatchdogController`

- Registers `/health` REST endpoint.
- Monitors for missed heartbeats and triggers disaster if not updated in time.

**Key Attributes:**
- `countdown_seconds`, `watchdog_period_seconds`

**Key Methods:**
- `health(request)`: Resets watchdog timer.
- `watchdog_timeout()`: Monitors and triggers disaster on timeout.

---

### 5. `network.py`

**Purpose**: WiFi connection and network health monitoring.

#### `NetworkController`

- Connects to WiFi using provided credentials.
- Monitors connection and triggers disaster on disconnect.

**Key Methods:**
- `connect()`: Activates and connects to WiFi.
- `network_monitor(config)`: Monitors and triggers disaster if network is lost.

---

## How to Use iotlib

### 1. Import and Initialize

from IoT.iotlib.config import RelaysConfiguration
from IoT.iotlib.network import NetworkController
from IoT.iotlib.watchdog import WatchdogController
from IoT.iotlib.disaster import DisasterController
import uasyncio as asyncio
from phew import server
app = server.Phew()
network = NetworkController(network_name="SSID", network_pass="password")
wlan = await asyncio.create_task(network.connect())
config = RelaysConfiguration(app=app, wlan=wlan, metrics_poll_url="http://remote/sensor")

### 2. Register and Validate APIs

- Each controller (e.g., Watchdog, Disaster) registers its own endpoints via `_apis_setup()`.
- The configuration object tracks all registered APIs.
- Use `validate_apis()` to ensure all required endpoints are present before starting main logic.

### 3. Disaster and Watchdog Monitoring

watchdog = WatchdogController(app=app, configuration=config)
disaster = DisasterController(configuration=config)
asyncio.create_task(watchdog.watchdog_timeout())
asyncio.create_task(disaster.disaster_monitor())

### 4. Network Monitoring

asyncio.create_task(network.network_monitor(config=config))

### 5. Task Management

- Use `async_utils.cancel_all(tasks)` to safely cancel all tasks during shutdown.

---

## Extending iotlib

- **Add new REST endpoints**: Extend `_apis` and `_apis_setup()` in your subclass.
- **Add new metrics or hardware**: Subclass `RelaysConfiguration` and add attributes.
- **Custom disaster logic**: Override `disaster_monitor()` in your controller.
- **Integrate with hardware-specific controllers**: Import and use iotlib base classes in your application modules.

---

## Example: Minimal Integration

from IoT.iotlib.config import RelaysConfiguration
from IoT.iotlib.watchdog import WatchdogController
from IoT.iotlib.disaster import DisasterController
from IoT.iotlib.network import NetworkController
import uasyncio as asyncio
from phew import server
app = server.Phew()
network = NetworkController("SSID", "password")
wlan = await asyncio.create_task(network.connect())
config = RelaysConfiguration(app=app, wlan=wlan, metrics_poll_url="http://remote/sensor")
watchdog = WatchdogController(app, config)
disaster = DisasterController(config)
asyncio.create_task(watchdog.watchdog_timeout())
asyncio.create_task(disaster.disaster_monitor())
asyncio.create_task(network.network_monitor(config))

---

## Design Philosophy

- **Separation of Concerns**: Each module handles a distinct aspect of IoT control.
- **Async-First**: All long-running operations are non-blocking.
- **Modular and Extensible**: Designed for subclassing and integration in diverse IoT scenarios.
- **Safety and Robustness**: Hardware is always left in a safe state on disaster or shutdown.

---

## License

MIT License. See `LICENSE` for details.

---

**iotlib is your foundation for building safe, robust, and maintainable MicroPython IoT solutions.**
