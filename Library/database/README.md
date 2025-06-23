# DatabaseManager

## Purpose

The DatabaseManager provides async PostgreSQL database management for the application:

- Manages async DB connections, sessions, and transactions
- Supports CRUD operations and state persistence
- Integrates with metrics, logging, and all components

## Features

- Async, thread-safe
- API for CRUD operations
- Prometheus metrics integration

## API

- `POST /database/` – Create a new record
- `GET /database/{record_id}` – Get a record by ID
- `GET /database/` – List all records
- `PUT /database/{record_id}` – Update a record by ID
- `DELETE /database/{record_id}` – Delete a record by ID

## Usage

Instantiate at app startup with your DB URL and inject into components as needed.
