"""
Schema registry for SchemasManager.

- Register all Pydantic schemas here for discovery and validation
"""

from pydantic import BaseModel, Field
from typing import Dict, Any

# Example schemas
class ExampleEvent(BaseModel):
    event_id: str = Field(..., example="evt-001")
    payload: Dict[str, Any]

class ExampleConfig(BaseModel):
    key: str
    value: Any

# Registry dictionary: name -> schema class
schema_registry = {
    "ExampleEvent": ExampleEvent,
    "ExampleConfig": ExampleConfig,
    # Add new schemas here as needed
}
