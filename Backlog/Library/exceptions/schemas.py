from pydantic import BaseModel
from typing import Dict, Optional

class ExceptionPayload(BaseModel):
    type: str
    message: str
    stacktrace: str
    service_name: str
    path: str
    method: str
    headers: Dict[str, str]
    timestamp: float
    context: Optional[Dict] = None
