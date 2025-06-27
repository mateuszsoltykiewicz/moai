from pydantic import BaseModel

class ApiStatusResponse(BaseModel):
    status: str
    message: str
