"""
Production-ready configuration validator for AppLib.

- Validates JSON configs against JSON Schema (Draft 2020-12).
- Raises clear errors for invalid configs.
- Can be used in CI/CD, service startup, or CLI tools.
"""

import json
from jsonschema import Draft202012Validator
from typing import Any, Dict

class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass

def load_json(path: str) -> Dict[str, Any]:
    """Load JSON from file."""
    with open(path, "r") as f:
        return json.load(f)

def validate_config(config: Dict[str, Any], schema: Dict[str, Any], config_name: str = "config"):
    """
    Validate a config dict against a schema.
    Raises ConfigValidationError if invalid.
    """
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(config), key=lambda e: e.path)
    if errors:
        msg = f"{config_name} validation failed:\n"
        for error in errors:
            msg += f" - {list(error.path)}: {error.message}\n"
        raise ConfigValidationError(msg)

def validate_config_file(config_path: str, schema_path: str, config_name: str = "config"):
    """
    Validate a config file against a schema file.
    """
    config = load_json(config_path)
    schema = load_json(schema_path)
    validate_config(config, schema, config_name)

# Example usage (for CLI or tests):
if __name__ == "__main__":
    import sys
    try:
        validate_config_file(
            sys.argv[1],  # config_path
            sys.argv[2],  # schema_path
            config_name=sys.argv[3] if len(sys.argv) > 3 else "Config"
        )
        print("Config validation succeeded.")
    except ConfigValidationError as e:
        print(e)
        exit(1)
