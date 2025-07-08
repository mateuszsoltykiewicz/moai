"""
Pydantic schemas for MetricsManager (for future extensibility).
"""

from pydantic import BaseModel
from typing import Dict, Any

class MetricInfo(BaseModel):
    name: str
    type: str
    description: str
    labels: Dict[str, Any] = {}
