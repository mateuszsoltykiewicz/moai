# ConfigManager

## Overview

**ConfigManager** is an async, schema-driven configuration loader and manager for modern Python microservices and applications.  
It supports both local file-based configuration and centralized configuration services, with hot-reload, environment variable overrides, and change notifications.

---

## Key Features

- **Async, Thread-Safe:** All operations are async and safe for concurrent use.
- **Schema Validation:** Uses Pydantic schemas to validate configuration structure and types.
- **Pluggable Providers:** Supports both local file-based and centralized (remote API) configuration sources.
- **Hot Reload:** Automatically reloads configuration on file change or remote update, and notifies listeners.
- **Environment Variable Overrides:** Allows dynamic overrides of config values via environment variables (e.g., for containerized deployments).
- **Change Listeners:** Register async callbacks to react to config changes at runtime.
- **Unified API:** Same interface for all providers—switch sources without changing your application code.

---

## Providers

- **FileConfigProvider:** Loads configuration from a local JSON file, supports environment variable overrides and hot-reload.
- **CentralConfigProvider:** Fetches configuration from a centralized config server (via HTTP/WebSocket), supports hot-reload and notifications.

---

## Usage

### 1. Choose and Initialize a Provider

from config.manager import ConfigManager
from config.providers.file import FileConfigProvider
from config.providers.central import CentralConfigProvider
from config.schemas import AppConfig
import os

if os.getenv(“CONFIG_SOURCE”) == “central”:
  provider = CentralConfigProvider(
    server_url=os.getenv(“CONFIG_SERVER_URL”),
    service_name=os.getenv(“SERVICE_NAME”),
    env=os.getenv(“ENV”)
  )
  else:
    provider = FileConfigProvider(
      config_path=“config/app_config.json”,
      env_prefix=“APP”
    )
config_manager = ConfigManager(provider=provider, schema=AppConfig) await config_manager.start()

### 2. Access and Use Configuration

config = await config_manager.get()
print(config.some_setting)

### 3. React to Hot-Reload Events

async def on_config_change(new_config):
  print(“Configuration updated!”, new_config)
config_manager.add_listener(“my_listener”, on_config_change)

### 4. Stop the Manager (on shutdown)

await config_manager.stop()

---

## Environment Variable Overrides

- Use environment variables with the prefix (e.g., `APP__DATABASE__HOST`) to override nested config values.
- Supports deep overrides for complex configurations.

---

## Example Directory Structure

config/
├── manager.py
├── provider.py
├── providers/
│   ├── file.py
│   └── central.py
├── schemas.py
├── exceptions.py
├── metrics.py
├── utils.py
└── README.md

---

## Extending

- Implement new providers (e.g., Consul, etcd, S3) by subclassing `ConfigProvider`.
- Add new schema fields and validation logic in `schemas.py`.
- Integrate with secrets managers (e.g., Vault) for secure config values.

---

## Best Practices

- Use schema validation to catch config errors early.
- Register listeners to handle config changes dynamically (no need to restart services).
- Use centralized config in production for consistency and auditability.
- Use environment variable overrides for containerized or cloud deployments.

---

## License

[Your License Here]

---

**ConfigManager powers robust, scalable, and observable configuration for your distributed applications.**
