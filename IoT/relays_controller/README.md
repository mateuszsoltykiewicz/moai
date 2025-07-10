# IoT/relays_controller — Comprehensive README

`relays_controller` is a **production-grade application module** for Raspberry Pi Pico W, built on top of the reusable `iotlib` MicroPython library. It provides a robust, async-driven heating controller with REST API, disaster safety, remote sensor integration, and hardware relay management.

---

## Features

- **HeatingController**: Implements REST API endpoints for heating control, initialization, and state reporting.
- **Remote Sensor Polling**: Periodically fetches metrics (temperature, water, gas leak) from a remote Pico W via REST API.
- **Disaster Detection**: Triggers safe shutdown on hardware, sensor, or network failure, and only when the system is initialized.
- **Dynamic API Registration**: All endpoints are registered at runtime and validated for completeness.
- **Async Task Management**: All operations are non-blocking and safely cancellable.
- **Safe Hardware Shutdown**: Ensures all relays are turned off on disaster or shutdown.
- **Comprehensive Comments**: Code is fully documented for clarity and maintainability.

---

## Directory Structure

relays_controller/
init.py
heating_controller.

---

## Module Overview

### 1. `heating_controller.py`

**Purpose**: Implements the main logic for heating control, relay management, REST API endpoints, remote metric polling, and disaster detection.

#### Key Methods

- `post_heating(request, state)`: Engage or disengage heating via POST.
- `get_heating(request)`: Get current heating status.
- `get_initialize(request)`: Get initialization state.
- `post_initialize(request, state)`: Initialize or de-initialize system.
- `heating_on()`: Async task to engage heating hardware.
- `heating_off()`: Async task to disengage heating hardware.
- `initialized()`: Async task to control pump based on initialization.
- `heating_monitor()`: Monitors temperature change; triggers disaster if not rising.
- `fetch_remote_metrics()`: Polls remote REST API for sensor metrics.
- `metrics_update_watchdog()`: Checks freshness of fetched metrics.
- `metrics_analyzer()`: Analyzes metrics for water/gas anomalies.

#### Example Usage

from IoT.iotlib.config import RelaysConfiguration
from .heating_controller import HeatingController
config = RelaysConfiguration(app=app, wlan=wlan, metrics_poll_url="http://remote/sensor")
heating_controller = HeatingController(app=app, configuration=config)

---

### 2. `main.py`

**Purpose**: Application entry point. Wires up all controllers, schedules async tasks, and starts the REST API server.

#### Key Steps

1. **Network Setup**: Connects to WiFi using `NetworkController`.
2. **Configuration**: Instantiates `RelaysConfiguration` with hardware and metrics settings.
3. **Controller Setup**: Initializes `WatchdogController`, `DisasterController`, and `HeatingController`.
4. **Async Task Scheduling**: Starts all monitoring, control, and polling tasks.
5. **Shutdown Handling**: Uses `ShutdownController` to coordinate safe shutdown and cleanup.
6. **Server Startup**: Runs the Phew server with all registered REST API endpoints.

#### Example Main

from IoT.iotlib.config import RelaysConfiguration
from IoT.iotlib.network import NetworkController
from IoT.iotlib.watchdog import WatchdogController
from IoT.iotlib.disaster import DisasterController
from .heating_controller import HeatingController
import uasyncio as asyncio
from phew import server
async def main(app):

#### Setup network, config, controllers

pass
app = server.Phew()
asyncio.run(main(app=app))

---

## Configuration

- **Pin Assignments**: Set in `RelaysConfiguration` (`PUMP_PIN`, `GAS_VALVE_PIN`, `SPARK_PIN`).
- **Remote Metrics URL**: Set `metrics_poll_url` to your remote sensor's REST endpoint.
- **Thresholds/Timeouts**: Adjust `target_temp`, `delta_temp_timeout`, `metrics_poll_interval`, etc., as needed.
- **API Endpoints**: All REST endpoints are registered and validated at runtime.

---

## Extending relays_controller

- **Add new REST endpoints**: Extend `_apis` and `_api_setup()` in `HeatingController`.
- **Add new hardware or metrics**: Extend `RelaysConfiguration` and update polling/analysis logic.
- **Integrate with other IoT devices**: Use `fetch_remote_metrics()` to connect to additional sensors.

---

## Example: Minimal Integration

from IoT.iotlib.config import RelaysConfiguration
from IoT.iotlib.network import NetworkController
from .heating_controller import HeatingController
import uasyncio as asyncio
from phew import server
app = server.Phew()
network = NetworkController("SSID", "password")
wlan = await asyncio.create_task(network.connect())
config = RelaysConfiguration(app=app, wlan=wlan, metrics_poll_url="http://remote/sensor")
heating_controller = HeatingController(app=app, configuration=config)
asyncio.create_task(heating_controller.heating_on())
asyncio.create_task(heating_controller.fetch_remote_metrics())

---

## Design Philosophy

- **Separation of Concerns**: All hardware and logic are modular and easily testable.
- **Async-First**: All operations are non-blocking and robust to failures.
- **Disaster Safety**: System is designed to fail safe and leave hardware in a safe state.
- **Extensible**: Easily add new sensors, endpoints, or control logic.

---

## License

MIT License. See `LICENSE` for details.

---

**relays_controller is your production-ready, extensible solution for safe, robust, and maintainable heating control on Raspberry Pi Pico W.**
