SensorsController
=================

Production-grade MicroPython firmware for Raspberry Pi Pico, designed to interface with multiple sensors via Grove Shield and PiCowbell CANBus (MCP2515).

Features
--------

- CANBus Communication: Uses MCP2515 via SPI for robust CAN communication.
- Sensor Support: Waveshare gas and flame sensors, DFRobot liquid level and water temperature sensors, water flow sensor YF-S402, and DHT-11 temperature/humidity sensor.
- Streaming Control: CANBus streaming is disabled by default and can be enabled/disabled via CAN commands.
- Hot-Reloadable JSON Configuration: All sensor mappings and operational parameters are configurable at runtime.
- REST API: Secure, token-protected API for configuration management and hot-reload.
- Hardware Watchdog: Ensures safe operation and automatic recovery on communication failure.
- Logging: Logs critical events to logs/events.log.
- Safe State Handling: Sensors initialized to safe state on boot, config reload, or error.
- Factory Config Recovery: Restores from factory_config.json if main config is missing or corrupt.

Directory Structure
-------------------

SensorsController/
├── README.md
├── boot.py
├── config.json
├── factory_config.json
├── lib/
│   ├── __init__.py
│   ├── canbus_handler.py
│   ├── config_manager.py
│   ├── grove_shield.py
│   ├── pins.py
│   ├── rest_api.py
│   ├── sensor_drivers/
│   │   ├── __init__.py
│   │   ├── dht11.py
│   │   ├── flame.py
│   │   ├── gas.py
│   │   ├── liquid_level.py
│   │   ├── water_temp.py
│   │   ├── flow.py
│   ├── watchdog.py
├── logs/
│   └── events.log
├── main.py
└── compile_mpy.sh

Pin Mapping
-----------

| Sensor           | Pin           |
|------------------|--------------|
| Flame Sensor     | D16          |
| Gas Sensor       | D16          |
| Liquid Level     | A1 (ADC1)    |
| Water Temp       | A1 (ADC1)    |
| Water Flow       | A2 (ADC0)    |
| DHT-11           | A2 (Digital) |
| CANBus SPI Bus   | SPI0         |
| CANBus CS Pin    | 17           |
| CANBus INT Pin   | 16           |

Configuration
-------------

- config.json: Main, hot-reloadable configuration file.
- factory_config.json: Immutable backup configuration for recovery.

Example config.json:
{
  "sensors": {
    "flame": {"type": "digital", "pin": "D16"},
    "gas": {"type": "digital", "pin": "D16"},
    "liquid_level": {"type": "analog", "pin": "A1"},
    "water_temp": {"type": "analog", "pin": "A1"},
    "flow": {"type": "digital", "pin": "A2"},
    "dht11": {"type": "digital", "pin": "A2"}
  },
  "canbus": {
    "spi_bus": 0,
    "cs_pin": 17,
    "int_pin": 16,
    "bitrate": 500000,
    "address": 18
  },
  "streaming_enabled": false,
  "api_token": "REPLACE_ME_WITH_A_SECURE_TOKEN"
}

REST API
--------

- GET /config: Returns current configuration.
- POST /config: Updates configuration (requires Authorization: Bearer <token> header).

CANBus Communication
--------------------

- Uses MCP2515 CAN controller via SPI.
- Supports commands to enable/disable streaming and update configuration.

Logging
-------

- Logs critical events (boot, config load, CAN commands, errors, sensor readings) to logs/events.log.
- Implement log rotation or archiving as needed.

Watchdog
--------

- Hardware watchdog is enabled to ensure system reliability.
- Resets the device and sets sensors to safe state on communication failure or main loop stall.

Compiling Python Files to .mpy Bytecode
---------------------------------------

For production deployments, compile all Python modules in lib/ to .mpy files to improve performance and protect source code.

Prerequisites

- Install mpy-cross compiler matching your MicroPython firmware version.

  git clone https://github.com/micropython/micropython.git
  cd micropython/mpy-cross
  make

- Ensure mpy-cross is in your PATH.

Automated Compilation

Use the provided compile_mpy.sh script:

  cd SensorsController
  chmod +x compile_mpy.sh
  ./compile_mpy.sh

Deployment

1. Upload all files from dist/lib/ to your Pico's /lib/ directory.
2. Upload main.py, boot.py, config.json, factory_config.json, and logs/ as needed.
3. Only compiled .mpy files and config/log files should be on the device for production.

Troubleshooting

- If you see ImportError: incompatible .mpy file, recompile with the correct mpy-cross version.
- Ensure all dependencies are compiled and present.

Deployment & Usage
------------------

1. Flash MicroPython firmware to your Pico.
2. Upload all necessary files.
3. Power on; device loads config, initializes sensors, starts CANBus and REST API.
4. Use REST API or CANBus commands to control streaming and update configuration.

Security
--------

- Set a strong API token in your config files.
- Restrict REST API access to trusted networks.
- Validate all configs before applying.
- Physically secure the device if security is critical.

References
----------

- MicroPython .mpy files documentation: https://docs.micropython.org/en/latest/reference/mpyfiles.html
- mpy-cross GitHub: https://github.com/micropython/micropython/tree/master/mpy-cross
- MCP2515 MicroPython drivers
- Microdot (REST API): https://github.com/miguelgrinberg/microdot

This project is designed for reliability, maintainability, and security in production Raspberry Pi Pico deployments.
