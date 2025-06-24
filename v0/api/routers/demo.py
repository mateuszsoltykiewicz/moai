"""
Demo router with custom hook execution
"""

from fastapi import APIRouter, Depends, Request
from schemas.api import StandardResponse, EndpointHookConfig
from api.dependencies import endpoint_processor, require_role
from exceptions.api import HookExecutionError

router = APIRouter()

# Example hook configuration
DEMO_HOOKS = EndpointHookConfig(
    pre_hook="api.hooks.demo.validate_demo_access",
    post_hook="api.hooks.demo.log_demo_activity"
)

@router.get(
    "/demo",
    response_model=StandardResponse,
    dependencies=[Depends(require_role("demo_user"))]
)
async def demo_endpoint(
    context: dict = Depends(
        lambda r: endpoint_processor(
            r,
            hook_config=DEMO_HOOKS
        )
    )
):
    """Endpoint with pre/post processing hooks"""
    try:
        # Main endpoint logic
        result = {"status": "processed"}
        
        # This would be executed automatically via post_hook
        # but we're showing explicit call for demo purposes
        await execute_hook(
            DEMO_HOOKS.post_hook,
            context["request"],
            user=context["user"],
            result=result
        )
        
        return StandardResponse(
            success=True,
            message="Demo completed",
            data=result
        )
    except HookExecutionError as e:
        return StandardResponse(
            success=False,
            message=str(e)
        )
