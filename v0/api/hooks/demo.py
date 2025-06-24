"""
Custom hook functions for demo endpoints
"""

from schemas.api import UserClaims
from exceptions.api import ForbiddenError
from requests import Request

def validate_demo_access(request: Request, user: UserClaims):
    """Custom pre-hook validation"""
    # Example: Restrict access during maintenance
    if request.app.state.maintenance_mode:
        raise ForbiddenError("Service in maintenance")
    
    # Example: Special demo user validation
    if "demo" not in user.roles:
        raise ForbiddenError("Demo access required")

async def log_demo_activity(request: Request, user: UserClaims, result: dict):
    """Custom post-hook processing"""
    # Async operation example
    logger = request.app.state.logger
    await logger.info(f"Demo completed by {user.sub}: {result}")
