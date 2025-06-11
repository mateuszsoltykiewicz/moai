"""
Production-ready configuration validator.

- Validates JSON configs against JSON Schema.
- Supports validation for all service configs.
- Raises clear errors for invalid configs.
"""

"""
Production-ready configuration validator for AppLib.

- Validates JSON configs against JSON Schema (Draft 2020-12).
- Raises clear errors for invalid configs.
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


"""
from AppLib.utils.config_validator import validate_config_file, ConfigValidationError

try:
    validate_config_file(
        "configs/dev/database.json",
        "schemas/validation/database.schema.json",
        config_name="Database Config"
    )
except ConfigValidationError as e:
    print(e)
    exit(1)

"""
