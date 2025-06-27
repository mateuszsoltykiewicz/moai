from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Span(BaseModel):
    trace_id: str
    span_id: str
    parent_id: str
    name: str
    start_time: float
    end_time: float
    attributes: Dict[str, Any] = {}

class TraceQueryResponse(BaseModel):
    trace_id: str
    spans: List[Span]
