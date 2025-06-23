# UtilsManager

## Purpose

The UtilsManager provides centralized utility and helper functions for the application:

- Robust logging setup for all components
- Common helpers and formatting utilities
- Integrates with FastAPI and all managers

## Features

- Production-ready logging (console, file, JSON)
- Async setup/shutdown
- API for diagnostics

## API

- `GET /utils/status` – Returns status of the UtilsManager

## Usage

Instantiate at app startup and inject into components as needed.
Use `utils_manager.get_logger()` to get a logger instance.
