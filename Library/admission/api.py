from fastapi import FastAPI, Request, HTTPException
from .manager import AdmissionManager
from .schemas import AdmissionReviewRequest, AdmissionReviewResponse
from Library.auth.manager import AuthManager  # For authentication
from Library.mtls.manager import MtlsManager  # For mTLS
from Library.logging import get_logger

app = FastAPI()
admission_manager = AdmissionManager()
auth_manager = AuthManager()
mtls_manager = MtlsManager()
logger = get_logger(__name__)

@app.post("/validate")
async def validate_pod(request: Request):
    try:
        # Authenticate request (mTLS or API key)
        if not await mtls_manager.verify_request(request):
            logger.warning("Invalid client certificate in admission webhook request")
            raise HTTPException(403, "Invalid client certificate")
        
        # Authorize (e.g., only allow specific services to call this webhook)
        if not await auth_manager.is_authorized(request):
            logger.warning("Unauthorized admission webhook request")
            raise HTTPException(403, "Unauthorized")
        
        # Process admission request
        admission_request_dict = await request.json()
        try:
            admission_request = AdmissionReviewRequest(**admission_request_dict)
        except Exception as e:
            logger.error(f"Malformed admission request: {e}", exc_info=True)
            raise HTTPException(400, "Malformed admission request")
        
        response = await admission_manager.validate_pod(admission_request)
        return response.dict()
    except Exception as e:
        logger.error(f"Admission webhook error: {e}", exc_info=True)
        raise HTTPException(500, "Internal error in admission webhook")
