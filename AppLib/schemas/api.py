"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional

class UserClaims(BaseModel):
    """Authenticated user claims"""
    sub: str
    roles: list[str]
    exp: int

class EndpointHookConfig(BaseModel):
    """Configuration for endpoint custom hooks"""
    pre_hook: Optional[str] = None
    post_hook: Optional[str] = None

class StandardResponse(BaseModel):
    """Standard API response format"""
    success: bool
    message: str 
    Optional[Dict[str, Any]] = None
