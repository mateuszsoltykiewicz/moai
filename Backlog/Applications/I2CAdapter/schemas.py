from pydantic import BaseModel
from typing import Literal

class CommandRequest(BaseModel):
    command: Literal["PowerCutOff", "PowerOn", "HeatingStart", "HeatingStop"]

class CommandResponse(BaseModel):
    result: str
