"""
Authentication API Router

- Token-based authentication (JWT)
- Configurable RBAC
- Pre/post hooks for authentication events
- Comprehensive metrics and telemetry
- Structured logging
- Password hashing with Argon2
- Refresh token rotation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Response
from datetime import timedelta
from typing import Dict, Any, Optional
from schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserInfoResponse,
    RefreshTokenRequest
)
from api.dependencies import base_endpoint_processor, require_role
from core.auth import AuthService, InvalidCredentialsError, TokenValidationError
from core.metrics import record_auth_operation
from core.tracing import AsyncTracer
from core.logging import logger
from core.config import get_config
import time

tracer = AsyncTracer("applib-auth").get_tracer()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        429: {"description": "Too Many Requests"}
    }
)

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return access/refresh tokens"
)
async def login(
    request: LoginRequest = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="auth:login",
            pre_hook="api.hooks.auth.before_login",
            post_hook="api.hooks.auth.after_login"
        )
    )
):
    """
    Authenticate user and issue tokens
    """
    start_time = time.monotonic()
    try:
        # Execute pre-hook validation
        if "validation_result" in context and not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )
        
        # Authenticate user
        with tracer.start_as_current_span("user_authentication"):
            config = get_config().auth
            auth_service = AuthService()
            tokens = await auth_service.authenticate_user(
                request.username,
                request.password,
                access_token_expire=timedelta(minutes=config.access_token_expire_minutes),
                refresh_token_expire=timedelta(days=config.refresh_token_expire_days)
            )
        
        # Set refresh token as HTTP-only cookie
        response = Response(content=tokens.model_dump_json())
        response.set_cookie(
            key="refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            secure=config.secure_cookies,
            samesite=config.cookie_samesite
        )
        
        duration = time.monotonic() - start_time
        record_auth_operation("login", duration, success=True)
        logger.info(f"User {request.username} logged in successfully")
        return response
        
    except InvalidCredentialsError:
        duration = time.monotonic() - start_time
        record_auth_operation("login", duration, success=False)
        logger.warning(f"Failed login attempt for user {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Generate new access token using refresh token"
)
async def refresh_token(
    request: RefreshTokenRequest = Body(None),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="auth:refresh",
            pre_hook="api.hooks.auth.before_refresh",
            post_hook="api.hooks.auth.after_refresh"
        )
    )
):
    """
    Refresh access token using a valid refresh token
    """
    start_time = time.monotonic()
    try:
        # Get refresh token from request body or cookie
        refresh_token = request.refresh_token if request else None
        if not refresh_token:
            refresh_token = context["request"].cookies.get("refresh_token")
        
        if not refresh_token:
            raise TokenValidationError("Missing refresh token")
        
        # Refresh tokens
        with tracer.start_as_current_span("token_refresh"):
            config = get_config().auth
            auth_service = AuthService()
            tokens = await auth_service.refresh_tokens(
                refresh_token,
                access_token_expire=timedelta(minutes=config.access_token_expire_minutes)
            )
        
        # Return new tokens
        duration = time.monotonic() - start_time
        record_auth_operation("refresh", duration, success=True)
        logger.info("Access token refreshed successfully")
        return tokens
        
    except TokenValidationError as e:
        duration = time.monotonic() - start_time
        record_auth_operation("refresh", duration, success=False)
        logger.warning(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout",
    description="Invalidate refresh token and clear cookies"
)
async def logout(
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="auth:logout",
            dependencies=[Depends(require_role("user"))]
        )
    )
):
    """
    Logout user and invalidate refresh token
    """
    start_time = time.monotonic()
    refresh_token = context["request"].cookies.get("refresh_token")
    
    # Invalidate token if exists
    if refresh_token:
        with tracer.start_as_current_span("token_invalidation"):
            auth_service = AuthService()
            await auth_service.invalidate_refresh_token(refresh_token)
    
    # Clear refresh token cookie
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie("refresh_token")
    
    duration = time.monotonic() - start_time
    record_auth_operation("logout", duration, success=True)
    logger.info(f"User {context['user'].sub} logged out")
    return response

@router.get(
    "/me",
    response_model=UserInfoResponse,
    summary="Get current user info",
    description="Retrieve information about the authenticated user"
)
async def get_current_user_info(
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="auth:me",
            dependencies=[Depends(require_role("user"))]
        )
    )
):
    """
    Get information about the authenticated user
    """
    start_time = time.monotonic()
    with tracer.start_as_current_span("user_info"):
        auth_service = AuthService()
        user_info = await auth_service.get_user_info(context["user"].sub)
    
    duration = time.monotonic() - start_time
    record_auth_operation("user_info", duration, success=True)
    return user_info
