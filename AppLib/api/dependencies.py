"""
Enhanced dependency system with custom hook execution
"""

from fastapi import Depends, Request, Header
from schemas.api import UserClaims, EndpointHookConfig
from exceptions.api import UnauthorizedError, ForbiddenError, HookExecutionError
from jose import JWTError, jwt
import importlib
import inspect

async def get_current_user(token: str = Header(...)) -> UserClaims:
    """Validate JWT and return user claims"""
    try:
        # Simplified validation - replace with your actual logic
        payload = jwt.decode(token, "SECRET", algorithms=["HS256"])
        return UserClaims(**payload)
    except JWTError:
        raise UnauthorizedError("Invalid token")

def require_role(role: str):
    """Dependency factory for role-based access"""
    async def role_checker(user: UserClaims = Depends(get_current_user)):
        if role not in user.roles:
            raise ForbiddenError(f"Requires {role} role")
        return user
    return role_checker

async def execute_hook(hook_path: str, request: Request, **kwargs):
    """Dynamically executes a hook function"""
    if not hook_path:
        return
    
    try:
        module_path, func_name = hook_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
        
        # Inspect parameters and pass only what's needed
        sig = inspect.signature(func)
        params = {}
        for name, param in sig.parameters.items():
            if name == "request":
                params[name] = request
            elif name in kwargs:
                params[name] = kwargs[name]
        
        # Execute sync or async hooks
        if inspect.iscoroutinefunction(func):
            return await func(**params)
        return func(**params)
    except Exception as e:
        raise HookExecutionError(f"Hook error: {str(e)}")

async def endpoint_processor(
    request: Request,
    hook_config: EndpointHookConfig = EndpointHookConfig(),
    user: UserClaims = Depends(get_current_user)
):
    """Default endpoint processor with hook execution"""
    # Execute pre-hook if configured
    await execute_hook(hook_config.pre_hook, request, user=user)
    
    # Return context for endpoint handler
    return {"user": user, "request": request}
