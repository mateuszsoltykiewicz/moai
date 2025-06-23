import pytest
from AppLib.utils.config_validator import validate_config, ConfigValidationError

def test_valid_config():
    config = {"host": "localhost", "port": 5432, "user": "u", "password": "p", "database": "d"}
    schema = {
        "type": "object",
        "properties": {
            "host": {"type": "string"},
            "port": {"type": "integer"},
            "user": {"type": "string"},
            "password": {"type": "string"},
            "database": {"type": "string"}
        },
        "required": ["host", "port", "user", "password", "database"]
    }
    validate_config(config, schema, config_name="TestConfig")

def test_invalid_config():
    config = {"host": 123, "port": "not-a-port"}
    schema = {
        "type": "object",
        "properties": {
            "host": {"type": "string"},
            "port": {"type": "integer"}
        },
        "required": ["host", "port"]
    }
    with pytest.raises(ConfigValidationError):
        validate_config(config, schema, config_name="TestConfig")