from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal

class RateLimitScope(str, Enum):
    USER = "user"
    IP = "ip"
    GLOBAL = "global"

class RateLimitConfigRequest(BaseModel):
    scope: RateLimitScope = Field(..., description="Scope for rate limiting (e.g., 'user', 'ip', 'global')")
    limit: int = Field(..., ge=1, description="Max requests allowed in the period (must be >= 1)")
    period_seconds: int = Field(..., ge=1, description="Period in seconds (must be >= 1)")

    class Config:
        schema_extra = {
            "example": {
                "scope": "user",
                "limit": 100,
                "period_seconds": 60
            }
        }

class RateLimitConfigResponse(BaseModel):
    scope: RateLimitScope = Field(..., description="Scope for rate limiting")
    limit: int = Field(..., ge=1, description="Max requests allowed in the period")
    period_seconds: int = Field(..., ge=1, description="Period in seconds")

    class Config:
        schema_extra = {
            "example": {
                "scope": "user",
                "limit": 100,
                "period_seconds": 60
            }
        }

class RateLimitStatusResponse(BaseModel):
    allowed: bool = Field(..., description="Is the request currently allowed?")
    remaining: int = Field(..., ge=0, description="Number of requests left in the current window")
    reset_in: int = Field(..., ge=0, description="Seconds until the rate limit resets")

    class Config:
        schema_extra = {
            "example": {
                "allowed": True,
                "remaining": 37,
                "reset_in": 12
            }
        }
