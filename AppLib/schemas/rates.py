from pydantic import BaseModel, Field

class RateLimitConfigRequest(BaseModel):
    scope: str = Field(..., description="Scope for rate limiting (e.g., 'user', 'ip', 'global')")
    limit: int = Field(..., description="Max requests allowed in the period")
    period_seconds: int = Field(..., description="Period in seconds")

class RateLimitConfigResponse(BaseModel):
    scope: str
    limit: int
    period_seconds: int

class RateLimitStatusResponse(BaseModel):
    allowed: bool
    remaining: int
    reset_in: int