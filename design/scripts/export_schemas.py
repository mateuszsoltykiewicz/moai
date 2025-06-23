"""
Export Pydantic model schemas as JSON Schema files for validation and documentation.

- This script should be run whenever you update or add Pydantic models.
- It will output JSON Schema files to the /schemas/validation/ directory.
- These schemas can be used for config validation, OpenAPI docs, or sharing with other teams.
"""

import json
from pathlib import Path

# Import all config and data models you want to export as JSON Schema
from models.config import (
    AppConfig,
    RoutersConfig,
    KafkaConfig,
    DatabaseConfig,
    PersistenceConfig,
    # Add more config models as needed
)
from models.schemas import (
    HealthCheckSchema,
    KafkaMessageSchema,
    UserSchema,
    UserCreateSchema,
    UserWithPostsSchema,
    # Add more data models as needed
)

# Map schema names to their corresponding Pydantic models
EXPORTS = {
    # Config section schemas
    "app_config": AppConfig,
    "routers_config": RoutersConfig,
    "kafka_config": KafkaConfig,
    "database_config": DatabaseConfig,
    "persistence_config": PersistenceConfig,
    # Data and API schemas
    "health_check": HealthCheckSchema,
    "kafka_message": KafkaMessageSchema,
    "user": UserSchema,
    "user_create": UserCreateSchema,
    "user_with_posts": UserWithPostsSchema,
    # Add more as needed
}

# Output directory for JSON Schemas
SCHEMA_DIR = Path("schemas/validation")
SCHEMA_DIR.mkdir(parents=True, exist_ok=True)

# Export each model's JSON Schema to a file
for name, model in EXPORTS.items():
    schema_path = SCHEMA_DIR / f"{name}.schema.json"
    with open(schema_path, "w") as f:
        # Use Pydantic's model_json_schema() for accurate, standards-compliant output
        json.dump(model.model_json_schema(), f, indent=2)
    print(f"Exported {name} schema to {schema_path}")

print("All schemas exported successfully.")
