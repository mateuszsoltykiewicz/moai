# CanbusManager

## Purpose

The CanbusManager provides async CANBus sensor streaming and configuration for the application:

- Manages CANBus interface and sensor configuration
- Streams sensor data (temperature, humidity, water level, gas, flame, etc.)
- Integrates with metrics, logging, alarms, and state management

## Features

- Async, thread-safe
- API for sensor streaming and discovery
- Prometheus metrics integration

## API

- `GET /canbus/stream` – Stream data for a configured sensor
- `GET /canbus/sensors` – List all configured sensor names

## Usage

Instantiate at app startup with config and inject into components as needed.
