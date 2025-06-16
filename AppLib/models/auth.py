from pydantic import BaseModel, Field
from typing import Optional

class AuthConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable token authentication for API routers")