# Core Module

This module provides foundational components for configuration, state management, and error handling.

## Configuration Management (`config.py`)

- Loads configuration from JSON files.
- Validates configuration using [Pydantic](https://docs.pydantic.dev/).
- Supports environment variable overrides for easy deployment customization.
- Raises clear, actionable errors on misconfiguration.

### Usage

from AppLib.core.config import ConfigLoader

Load config from a JSON file

config_loader = ConfigLoader(“configs/dev/app_config.json”) config = config_loader.get()

Access Kafka config
print(config.kafka.bootstrap_servers)

## Hot Reload and Dynamic Updates

- The ConfigService watches config files for changes and reloads them automatically.
- All reloads are validated before being applied.
- Register listeners to react to config changes:

config_service.register_listener(on_config_update)

- You can also trigger reloads via API or CLI.

### Environment Variable Overrides

You can override any config value with an environment variable.  
For example, to override the Kafka bootstrap servers:

export APP__KAFKA__BOOTSTRAP_SERVERS=“kafka:9092”


### Schema Extension

To add new configuration sections, extend the `AppConfig` Pydantic model and add corresponding JSON keys.

## Error Handling

- Invalid or missing configuration raises clear exceptions.
- All errors are logged for troubleshooting.

## Best Practices

- Keep sensitive values (like passwords) out of your repo; use environment variables or Vault.
- Validate your config before deploying to production.

---
