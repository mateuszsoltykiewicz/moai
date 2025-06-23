# SessionsManager

## Purpose

The SessionsManager provides centralized, async session management for the application:

- Manages sessions for adapters, hardware, and other resources
- Supports session creation, retrieval, update, and deletion
- Integrates with metrics and logging

## Features

- Async, thread-safe
- API for CRUD operations on sessions
- Prometheus metrics integration

## API

- `POST /sessions/` – Create a new session
- `PUT /sessions/{session_id}` – Update a session
- `GET /sessions/{session_id}` – Retrieve a session
- `DELETE /sessions/{session_id}` – Delete a session
- `GET /sessions/` – List all sessions

## Usage

Instantiate at app startup and inject into components as needed.
