from pydantic import BaseModel, Field
from typing import Dict, Optional, List

class SecurityConfig(BaseModel):
    enabled: bool = Field(True, description="Enable security system")
    require_authentication: bool = Field(True, description="Require authentication for all endpoints")
    require_https: bool = Field(True, description="Require HTTPS connections")
    rbac_enabled: bool = Field(True, description="Enable Role-Based Access Control")
    default_roles: List[str] = Field(["user"], description="Default roles for endpoints without specific configuration")
    endpoint_roles: Dict[str, List[str]] = Field(
        {},
        description="Endpoint-specific role requirements (format: 'router:endpoint')"
    )