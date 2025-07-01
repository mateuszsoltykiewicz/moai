from pydantic import BaseModel, Field

class DisasterStatusResponse(BaseModel):
    active: bool = Field(..., description="Is a disaster currently detected?")
