"""
mTLS API Router

- Status check
- Example secure endpoint
"""

from fastapi import APIRouter, Request, Depends
from models.schemas import MTLSStatusResponse
from api.dependencies import get_current_user

router = APIRouter(tags=["mtls"])

def get_client_cert_info(request: Request) -> Optional[str]:
    return request.headers.get("x-client-cert")

@router.get(
    "/status",
    response_model=MTLSStatusResponse,
    summary="Check mTLS status"
)
async def mtls_status(request: Request, user=Depends(get_current_user)):
    cert_info = get_client_cert_info(request)
    if cert_info:
        return MTLSStatusResponse(mtls=True, client_cert=cert_info)
    return MTLSStatusResponse(mtls=False, message="No client certificate presented.")

@router.get(
    "/secure",
    summary="Example mTLS-protected endpoint"
)
async def mtls_secure_endpoint(request: Request, user=Depends(get_current_user)):
    cert_info = get_client_cert_info(request)
    return {
        "message": "This endpoint requires mTLS (enforced by proxy)",
        "client_cert": cert_info
    }
