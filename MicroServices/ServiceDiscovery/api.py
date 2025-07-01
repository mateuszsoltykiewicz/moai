from fastapi import APIRouter, Depends
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import ServiceDiscoveryManager
from .schemas import ServiceInfo, ServiceListResponse
from typing import List

logger = get_logger(__name__)
router = APIRouter(prefix="/discovery", tags=["discovery"])

@router.get("/services", response_model=ServiceListResponse, dependencies=[Depends(require_jwt_and_rbac)])
async def list_services():
    return await ServiceDiscoveryManager.list_services()

@router.get("/allowed", response_model=List[str], dependencies=[Depends(require_jwt_and_rbac)])
async def get_allowed_services():
    return await ServiceDiscoveryManager.get_allowed_services()
