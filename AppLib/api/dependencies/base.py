"""
Base Endpoint Processor Dependency

- Executes optional pre- and post-hooks (by dotted path)
- Supports additional dependencies (e.g., RBAC, validation)
- Returns a context dictionary for use in endpoints
- Designed for use as a FastAPI dependency
- Handles async and sync hooks/dependencies
"""

from typing import Dict, Any, List, Optional
from fastapi import Request
import importlib
import inspect
import logging

logger = logging.getLogger(__name__)

async def base_endpoint_processor(
    request: Request,
    pre_hook: Optional[str] = None,
    post_hook: Optional[str] = None,
    dependencies: Optional[List[Any]] = None
) -> Dict[str, Any]:
    """
    FastAPI dependency for endpoint pre/post processing and dependency chaining.

    Args:
        request: FastAPI Request object.
        pre_hook: Dotted path to a pre-processing hook function (optional).
        post_hook: Dotted path to a post-processing hook function (optional).
        dependencies: List of FastAPI Depends-wrapped callables (optional).

    Returns:
        context: dict with request, hook results, and dependency results.
    """
    context = {"request": request}

    # --- Execute additional dependencies if provided ---
    if dependencies:
        for dep in dependencies:
            dep_callable = dep.dependency
            try:
                if inspect.iscoroutinefunction(dep_callable):
                    result = await dep_callable(request)
                else:
                    result = dep_callable(request)
                # Store result by function name (or override as needed)
                context[dep_callable.__name__] = result
            except Exception as e:
                logger.error(f"Dependency {dep_callable.__name__} failed: {e}")
                context[f"{dep_callable.__name__}_error"] = str(e)

    # --- Helper to load and execute a hook by dotted path ---
    async def execute_hook(hook_path: Optional[str]):
        if not hook_path:
            return None
        try:
            module_path, func_name = hook_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            sig = inspect.signature(func)
            params = {}
            for name in sig.parameters:
                if name == "request":
                    params[name] = request
                elif name in context:
                    params[name] = context[name]
            if inspect.iscoroutinefunction(func):
                return await func(**params)
            else:
                return func(**params)
        except Exception as e:
            logger.error(f"Hook {hook_path} execution failed: {e}")
            return {"hook_error": str(e)}

    # --- Execute pre-hook (if any) ---
    pre_result = await execute_hook(pre_hook)
    if pre_result is not None:
        context["validation_result"] = pre_result if isinstance(pre_result, dict) else {"result": pre_result}

    # --- Store post-hook path for endpoint to call after main logic (if desired) ---
    context["post_hook"] = post_hook

    return context
