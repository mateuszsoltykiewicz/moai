# Config Validator

- Validates any service config using JSON Schema.
- Raises `ConfigValidationError` with details on failure.
- Integrate in your config loader or CI pipeline.

## Features

- Validates JSON configs using JSON Schema (Draft 2020-12)
- Clear error messages for invalid configs
- Integrates with config loader for startup/reload validation

## Usage

from AppLib.utils.config_validator import validate_config_file
validate_config_file(
  “configs/dev/database.json”,
  “schemas/validation/database.schema.json”,
  config_name=“Database Config”
)


## Best Practices

- Validate all configs before startup.
- Keep schemas in `schemas/validation/`.
- Use strict schemas for reliability.


## Example Error

Database Config validation failed:
	-	‘host’: ‘localhost’ is not of type ‘integer’
	-	‘port’: ‘not-a-port’ is not of type ‘integer’


## Testing

- Add unit tests for valid/invalid configs.
- Test all config types (Kafka, DB, etc.).

---
