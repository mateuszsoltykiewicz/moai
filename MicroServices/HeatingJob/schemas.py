from pydantic import BaseModel, Field
from typing import Optional

class HeatingJobTriggerRequest(BaseModel):
    operator: str = Field(..., example="controller")
    params: Optional[dict] = None

class HeatingJobStatusResponse(BaseModel):
    running: bool
    last_temp: Optional[float]
