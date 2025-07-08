from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class ExceptionPayload(BaseModel):
    type: str = Field(..., example="ValueError")
    message: str = Field(..., example="Invalid input")
    stacktrace: str = Field(..., example="Traceback (most recent call last): ...")
    service_name: str = Field(..., example="payment-service")
    path: Optional[str] = Field(None, example="/payments")
    method: Optional[str] = Field(None, example="POST")
    headers: Optional[Dict[str, str]] = None
    timestamp: float = Field(..., example=1698765432.123)
    context: Optional[Dict[str, Any]] = None

class ExceptionQueryResponse(BaseModel):
    exceptions: List[ExceptionPayload]
