RelaysController
================

Production-grade MicroPython firmware for Raspberry Pi Pico, designed to control 4 relays via GPIO18-21.
This controller receives commands over I2C (as a slave device), supports hot-reloadable JSON configuration,
exposes a secure REST API for configuration, and implements robust logging and watchdog safety.

Features
--------

- I2C Slave Communication: Listens for commands from an I2C master (e.g., Raspberry Pi Compute Module 5).
- Relay Control: 4 relays on GPIO18, 19, 20, 21.
- Hot-Reloadable Config: All mappings and states are set via config.json, which can be updated at runtime.
- REST API: Secure, token-protected API for config management and hot-reload.
- Hardware Watchdog: Ensures safe state and automatic recovery on error.
- Logging: Logs all critical events to logs/events.log.
- Safe State Handling: Relays are always set to a safe state on boot, config reload, or error.
- Factory Config Recovery: If config is missing/corrupt, restores from factory_config.json.

Directory Structure
-------------------

RelaysController/
├── README.md
├── boot.py
├── config.json
├── factory_config.json
├── lib/
│   ├── __init__.py
│   ├── config_manager.py
│   ├── i2c_handler.py
│   ├── i2c_slave.py        # From rp2040-i2c-slave
│   ├── pins.py
│   ├── relay_driver.py
│   ├── rest_api.py
│   └── watchdog.py
├── logs/
│   └── events.log
├── main.py
└── compile_mpy.sh

Pinout
------

| Function   | GPIO |
|------------|------|
| Relay 1    | 18   |
| Relay 2    | 19   |
| Relay 3    | 20   |
| Relay 4    | 21   |
| I2C SDA    | 16   |
| I2C SCL    | 17   |

Configuration
-------------

- config.json: Main, hot-reloadable config (relay mapping, API token, etc.)
- factory_config.json: Immutable backup config for recovery.

Example config.json:
{
  "relay_pins": [18, 19, 20, 21],
  "command_map": {
    "ON_1": 0,
    "OFF_1": 1,
    "ON_2": 2,
    "OFF_2": 3
  },
  "default_state": [0, 0, 0, 0],
  "api_token": "REPLACE_ME_WITH_A_SECURE_TOKEN"
}

REST API
--------

- GET /config: Returns current config.
- POST /config: Updates config (requires Authorization: Bearer <token> header).

I2C Communication
-----------------

- Slave address: 0x43 (configurable in lib/pins.py)
- Protocol: Master sends a command string (e.g., "ON_1"), Pico responds with b"OK" or b"ERR".

Logging
-------

- All critical events (boot, config load, I2C commands, errors) are appended to logs/events.log.
- Rotate or archive logs as needed for your deployment.

Watchdog
--------

- Hardware watchdog is always enabled.
- If the main loop stalls or communication is lost, the Pico resets and relays revert to a safe state.

Compiling Python Files to .mpy Bytecode
---------------------------------------

For production deployments, compile all Python modules in lib/ to .mpy files. This improves performance and protects your source code.

Prerequisites

- Install the mpy-cross compiler matching your Pico's MicroPython version.

  git clone https://github.com/micropython/micropython.git
  cd micropython/mpy-cross
  make

  Ensure mpy-cross is in your PATH.

Automated Compilation

Use the provided script:

  cd RelaysController
  chmod +x compile_mpy.sh
  ./compile_mpy.sh

- This will compile all .py files in lib/ to .mpy and place them in dist/lib/ for deployment.

Deployment

1. Upload all files from dist/lib/ to your Pico's /lib/ directory.
2. Upload main.py, boot.py, config.json, factory_config.json, and logs/ as needed.
3. Only compiled .mpy files and config/log files should be on the device for production.

Troubleshooting

- If you see ImportError: incompatible .mpy file, recompile with the correct mpy-cross version.
- If a module fails to import, ensure all dependencies are present and compiled.

Deployment & Usage
------------------

1. Flash MicroPython firmware to your Pico.
2. Upload all necessary files as described above.
3. Power on. The device will load config, set relays to a safe state, and start I2C/REST API.
4. Use the REST API or I2C master to control relays and update configuration.

Security
--------

- Always set a strong API token in your config files.
- Only expose REST API on trusted networks.
- Validate all configs before applying.
- Physically secure the device if security is critical.

References
----------

- MicroPython .mpy files documentation: https://docs.micropython.org/en/latest/reference/mpyfiles.html
- mpy-cross GitHub: https://github.com/micropython/micropython/tree/master/mpy-cross
- rp2040-i2c-slave: https://github.com/ifurusato/rp2040-i2c-slave
- Microdot (REST API): https://github.com/miguelgrinberg/microdot

This project is designed for reliability, maintainability, and security in production Raspberry Pi Pico deployments.
