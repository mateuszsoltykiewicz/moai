# /Python/libraries/core/schema_validation/__init__.py
import jsonschema

def validate_schema(instance, schema):
    jsonschema.validate(instance=instance, schema=schema)
