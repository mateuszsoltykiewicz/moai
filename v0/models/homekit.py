from pydantic import BaseModel, Field
from typing import List, Dict, Any

class HomeKitAccessory(BaseModel):
    name: str
    category: str
    services: List[str]
    config: Dict[str, Any] = Field(default_factory=dict)
