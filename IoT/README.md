# IoT Pico W Heating Controller System

This repository provides a **modular, production-grade IoT system** for Raspberry Pi Pico W, featuring a reusable MicroPython library (`iotlib`) and a specific heating controller application (`relays_controller`). The solution is robust, async-driven, and designed for maintainability, disaster safety, and remote sensor integration.

---

## Directory Structure

.
├── README.md
├── __init__.py
├── iotlib
│   ├── __init__.py
│   ├── configuration.py
│   ├── disaster.py
│   ├── network.py
│   ├── shutdown.py
│   └── watchdog.py
├── relays_controller
│   ├── __init__.py
│   ├── configuration.py
│   ├── heating_controller.py
│   └── main.py
└── sensors_controller
    └── main.py

4 directories, 13 files

---

## IoT/iotlib

**Reusable MicroPython IoT library for any controller application.**

### Features

- **Configuration Management**: Central state, disaster flags, API registration.
- **Async Utilities**: Task management, cancellation helpers.
- **Disaster Controller**: Monitors for disaster, coordinates shutdown.
- **Watchdog Controller**: Heartbeat endpoint and missed-heartbeat detection.
- **Network Controller**: WiFi connect and monitoring.
- **Hardware Agnostic**: No direct pin assignments; reusable across projects.

### Usage

from IoT.iotlib.config import Configuration, RelaysConfiguration
from IoT.iotlib.async_utils import cancel_all
from IoT.iotlib.disaster import DisasterController
from IoT.iotlib.watchdog import WatchdogController
from IoT.iotlib.network import NetworkController
config = RelaysConfiguration(app=app, wlan=wlan, metrics_poll_url="http://...")
watchdog = WatchdogController(app=app, configuration=config)
disaster = DisasterController(configuration=config)
network = NetworkController(network_name="SSID", network_pass="password")

### Extending

- Add new controllers as modules in `iotlib/`.
- Extend `Configuration` for device-specific state.
- Use provided controllers as building blocks for custom IoT solutions.

---

## IoT/relays_controller

**Application for heating control on Pico W using REST API and remote sensor polling.**

### Features

- **HeatingController**: REST API, relay management, remote sensor polling.
- **Dynamic API Registration**: Endpoints registered and validated at runtime.
- **Disaster Handling**: Safe shutdown on hardware/sensor/network failures.
- **Remote Sensor Integration**: Polls metrics from another Pico W; triggers disaster on loss of connection (only if initialized).
- **Production-Ready**: All async tasks are cancellable, hardware is left safe, code is fully commented.

### Configuration

- **Pin Assignments**: Set in `RelaysConfiguration`.
- **Remote Metrics URL**: Set `metrics_poll_url` to your remote sensor endpoint.
- **Thresholds/Timeouts**: Adjust `target_temp`, `delta_temp_timeout`, etc.

### Running the Application

from IoT.iotlib.config import RelaysConfiguration
from IoT.iotlib.network import NetworkController
from IoT.iotlib.watchdog import WatchdogController
from IoT.iotlib.disaster import DisasterController
from .heating_controller import HeatingController
import uasyncio as asyncio
from phew import server
async def main(app):

#### Setup network, config, controllers

#### (see relays_controller/main.py)

pass
app = server.Phew()
asyncio.run(main(app=app))

---

## Deployment Manual (MacBook + Visual Studio Code)

### Prerequisites

- **Raspberry Pi Pico W** with MicroPython firmware.
- **MacBook** with Python 3.9+ and VS Code.
- **MicroPico** (or Pico-W-Go) extension in VS Code.
- USB cable.

### Project Preparation

1. **Clone or copy** your `/IoT` project folder to your Mac.
2. Ensure your directory structure matches the above.

### Flashing MicroPython Firmware

1. Download the latest MicroPython UF2 for Pico W from [micropython.org/download/rp2-pico-w/](https://micropython.org/download/rp2-pico-w/).
2. Connect Pico W to your Mac while holding **BOOTSEL**.
3. Drag the `.uf2` file onto the `RPI-RP2` USB drive.
4. Pico W will reboot as a MicroPython device.

### VS Code Setup and Extensions

1. Open VS Code.
2. Install **MicroPico** (or **Pico-W-Go**) from Extensions.
3. Open your `/IoT` project folder in VS Code.
4. Use the extension to configure your project for MicroPython.

### Uploading Code to Pico W

1. In VS Code, use the file explorer to create `iotlib` and `relays_controller` folders on the Pico W.
2. Right-click files/folders and select **"Upload to Pico"** to transfer your code.
3. Ensure `main.py` is present and set as the main script (right-click → "Set as main script" or copy to root as `main.py`).

### Running and Monitoring

- Use the **Run** button or right-click → "Run current file" to start your app.
- Open the REPL or terminal in VS Code to monitor output and debug.
- Your REST API and controllers should now be running on the Pico W.

### Troubleshooting

- If you see `ImportError`, check that all folders and files are present and correctly named.
- For missing dependencies or modules, ensure all library files are uploaded to the Pico W.
- Use the REPL or Thonny for further debugging if needed.

---

## License

This project is provided under the MIT License. See the `LICENSE` file for details.

---

**You are ready to build, deploy, and extend your IoT solutions using this modular, production-grade codebase!**
