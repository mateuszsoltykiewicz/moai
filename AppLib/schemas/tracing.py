from pydantic import BaseModel, Field
from typing import List, Dict, Any

class TraceInfo(BaseModel):
    trace_id: str = Field(..., example="123abc")
    span_id: str = Field(..., example="456def")
    parent_span_id: str = Field(..., example="789ghi")
    attributes: Dict[str, Any] = Field(default_factory=dict)
    name: str = Field(..., example="operation_name")
    start_time: str
    end_time: str
    status: str
