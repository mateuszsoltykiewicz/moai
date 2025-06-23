from pydantic import BaseModel, Field
from typing import Optional, List

class UserProfile(BaseModel):
    user_id: str
    display_name: str
    email: str
    roles: List[str] = Field(default_factory=list)

class UserSettings(BaseModel):
    user_id: str
    preferences: Dict[str, Any] = Field(default_factory=dict)
