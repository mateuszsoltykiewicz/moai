from pydantic import BaseModel
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None

class UserInfoResponse(BaseModel):
    id: str
    username: str
    email: str
    roles: list[str]
    created_at: datetime
