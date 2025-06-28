from fastapi import APIRouter, HTTPException, Body, Depends, Request
from .manager import ServiceRegistryManager
from .schemas import (
    RegisterRequest, HeartbeatRequest, DeregisterRequest,
    ServiceListResponse, ServiceInstanceResponse
)
from .exceptions import ServiceNotFoundError, InstanceNotFoundError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/registry", tags=["registry"])
registry_manager = ServiceRegistryManager()

@router.post("/register", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "registry", "write"))])
async def register_service(req: RegisterRequest = Body(...)):
    await registry_manager.register(req)
    return {"result": "ok"}

@router.post("/heartbeat", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "registry", "write"))])
async def heartbeat(req: HeartbeatRequest = Body(...)):
    try:
        await registry_manager.heartbeat(req)
        return {"result": "ok"}
    except InstanceNotFoundError as e:
        logger.warning(f"Instance not found: {e}")
        raise HTTPException(404, str(e))

@router.post("/deregister", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "registry", "write"))])
async def deregister(req: DeregisterRequest = Body(...)):
    try:
        await registry_manager.deregister(req)
        return {"result": "ok"}
    except InstanceNotFoundError as e:
        logger.warning(f"Instance not found: {e}")
        raise HTTPException(404, str(e))

@router.get("/services", response_model=ServiceListResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "registry", "read"))])
async def list_services():
    services = await registry_manager.list_services()
    return {"services": services}

@router.get("/instance/{service_name}/{instance_id}", response_model=ServiceInstanceResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "registry", "read"))])
async def get_instance(service_name: str, instance_id: str):
    try:
        instance = await registry_manager.get_service_instance(service_name, instance_id)
        return {"instance": instance}
    except InstanceNotFoundError as e:
        logger.warning(f"Instance not found: {e}")
        raise HTTPException(404, str(e))
