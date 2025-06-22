from fastapi import Depends, HTTPException, Request
from core.config import get_config

def require_role(permission: str):
    async def checker(request: Request):
        config = get_config().security
        
        # Bypass if security disabled
        if not config.enabled:
            return
        
        # Check if user has permission
        user = request.state.user  # Assuming user is set in middleware
        if permission not in user.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Missing permission: {permission}"
            )
    return Depends(checker)
