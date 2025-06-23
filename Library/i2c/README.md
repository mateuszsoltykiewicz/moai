# I2CManager

## Purpose

The I2CManager provides async I2C hardware and GPIO control for the application:

- Manages I2C bus and GPIO relay/valve/pump control
- Supports hardware configuration and state monitoring
- Streams events to Kafka and persists to Database if enabled

## Features

- Async, thread-safe
- API for hardware control and status
- Prometheus metrics integration

## API

- `POST /i2c/control` – Control a relay, valve, or pump via GPIO
- `GET /i2c/status` – Get the status of a relay or I2C device
- `GET /i2c/devices` – List all known relay and I2C device names

## Usage

Instantiate at app startup with config and inject into components as needed.
