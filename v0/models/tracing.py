from pydantic import BaseModel, Field
from typing import Optional, Dict

class TraceContext(BaseModel):
    trace_id: str
    span_id: str
    parent_id: Optional[str] = None
    baggage: Optional[Dict[str, str]] = None

class SpanInfo(BaseModel):
    name: str
    start_time: float
    end_time: float
    attributes: Optional[Dict[str, Any]] = None
