from pydantic import BaseModel

class SecretRotateRequest(BaseModel):
    path: str

class SecretRotateResponse(BaseModel):
    path: str
    new_version: int
