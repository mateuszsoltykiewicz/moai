"""
Dependency for endpoint processing with hooks
"""

from fastapi import Depends, Request
from api.hooks.registry import hook_registry
from core.logging import logger
from typing import Dict, Any, Optional

async def endpoint_processor(
    request: Request,
    pre_hook: Optional[str] = None,
    post_hook: Optional[str] = None
) -> Dict[str, Any]:
    """
    Endpoint processor with configurable pre/post hooks
    
    Returns:
        context: Dictionary with processing results
    """
    context = {"request": request}
    
    # Execute pre-hook if configured
    if pre_hook:
        try:
            hook_func = hook_registry.load_from_path(pre_hook)
            pre_result = await hook_func(request)
            context["pre_hook_result"] = pre_result
            context.update(pre_result or {})
        except Exception as e:
            logger.error(f"Pre-hook {pre_hook} failed: {str(e)}")
            context["pre_hook_error"] = str(e)
    
    return context
