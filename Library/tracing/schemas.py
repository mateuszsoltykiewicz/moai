"""
Pydantic schemas for TracingManager (for diagnostics endpoints).
"""

from pydantic import BaseModel
from typing import Dict, Any

class TraceInfo(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str
    attributes: Dict[str, Any]
    name: str
    start_time: str
    end_time: str
    status: str
