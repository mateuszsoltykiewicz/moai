from fastapi import APIRouter, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from .manager import CentralStateRegistry
from .schemas import ServiceState

API_KEY_NAME = "X-API-Key"
api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_scheme)):
    if not api_key or api_key != "YOUR_SECURE_API_KEY":  # Replace with Vault integration
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

router = APIRouter(prefix="/central_state", tags=["central_state"])

central_state_registry: CentralStateRegistry = None  # Injected at startup

@router.post("/register", dependencies=[Depends(validate_api_key)])
async def register_service(state: ServiceState):
    try:
        await central_state_registry.register_or_update(state)
        return {"result": "ok"}
    except Exception as e:
        raise HTTPException(500, f"Registration failed: {str(e)}")

@router.get("/services", dependencies=[Depends(validate_api_key)])
async def list_services():
    try:
        return await central_state_registry.list_services()
    except Exception as e:
        raise HTTPException(500, f"Service listing failed: {str(e)}")

@router.get("/service/{name}", dependencies=[Depends(validate_api_key)])
async def get_service(name: str):
    try:
        svc = await central_state_registry.get_service(name)
        if not svc:
            raise HTTPException(404, f"Service {name} not found")
        return svc
    except Exception as e:
        raise HTTPException(500, f"Service retrieval failed: {str(e)}")
