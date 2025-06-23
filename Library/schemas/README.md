# SchemasManager

## Purpose

The SchemasManager provides centralized Pydantic schema management for the application:

- Registers and provides access to all Pydantic schemas
- Supports schema validation, versioning, and dynamic loading
- Integrates with API documentation and other components

## Features

- Async, thread-safe
- API for schema discovery and validation
- Prometheus metrics integration

## API

- `GET /schemas/` – List all registered schema names
- `GET /schemas/{schema_name}` – Get a schema definition by name

## Usage

Instantiate at app startup and inject into components as needed.
Register new schemas in `schemas/registry.py`.
