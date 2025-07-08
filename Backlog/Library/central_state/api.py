from fastapi import APIRouter, HTTPException, Depends, Request
from .manager import CentralStateRegistry
from .schemas import ServiceState
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/central_state", tags=["central_state"])

central_state_registry: CentralStateRegistry = None  # Injected at startup

@router.post("/register", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "central_state", "write"))])
async def register_service(state: ServiceState):
    try:
        await central_state_registry.register_or_update(state)
        return {"result": "ok"}
    except Exception as e:
        logger.error(f"Service registration failed: {e}", exc_info=True)
        raise HTTPException(500, f"Registration failed: {str(e)}")

@router.get("/services", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "central_state", "read"))])
async def list_services():
    try:
        return await central_state_registry.list_services()
    except Exception as e:
        logger.error(f"Service listing failed: {e}", exc_info=True)
        raise HTTPException(500, f"Service listing failed: {str(e)}")

@router.get("/service/{name}", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "central_state", "read"))])
async def get_service(name: str):
    try:
        svc = await central_state_registry.get_service(name)
        if not svc:
            logger.warning(f"Service not found: {name}")
            raise HTTPException(404, f"Service {name} not found")
        return svc
    except Exception as e:
        logger.error(f"Service retrieval failed: {e}", exc_info=True)
        raise HTTPException(500, f"Service retrieval failed: {str(e)}")
