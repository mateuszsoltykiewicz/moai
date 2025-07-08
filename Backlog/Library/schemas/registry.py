from pydantic import BaseModel, Field
from typing import Dict, Any

class ExampleEventV1(BaseModel):
    event_id: str = Field(..., example="evt-001")
    payload: Dict[str, Any]

class ExampleEventV2(BaseModel):
    event_id: str = Field(..., example="evt-001")
    payload: Dict[str, Any]
    timestamp: str = Field(..., example="2025-06-27T17:00:00Z")

schema_registry = {
    "ExampleEvent:v1": ExampleEventV1,
    "ExampleEvent:v2": ExampleEventV2,
    # Add more schemas here
}
