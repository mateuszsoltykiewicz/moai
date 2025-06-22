"""
Configurable security middleware for FastAPI
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import get_config
from core.logging import logger

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        config = get_config().security
        
        # Enforce HTTPS if configured
        if config.require_https and request.url.scheme != "https":
            logger.warning(f"Insecure request blocked: {request.url}")
            raise HTTPException(
                status_code=400, 
                detail="HTTPS required"
            )
        
        # Skip authentication for public endpoints
        if not config.require_authentication:
            return await call_next(request)
        
        # Authentication check would go here
        # ... (implementation depends on your auth system)
        
        return await call_next(request)

async def authentication_middleware(request: Request, call_next):
    # Skip authentication for public endpoints
    if request.url.path in ["/auth/login", "/auth/refresh"]:
        return await call_next(request)
    
    # Extract and verify access token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing access token")
    
    token = auth_header.split(" ")[1]
    try:
        user = await AuthService().validate_access_token(token)
        request.state.user = user
    except TokenValidationError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    return await call_next(request)

