from fastapi import APIRouter, HTTPException
from .manager import CentralStateRegistry
from .schemas import ServiceState

router = APIRouter(prefix="/central_state", tags=["central_state"])
central_state_registry = CentralStateRegistry()

@router.post("/register")
async def register_service(state: ServiceState):
    await central_state_registry.register_or_update(state)
    return {"result": "ok"}

@router.get("/services")
async def list_services():
    return await central_state_registry.list_services()

@router.get("/service/{name}")
async def get_service(name: str):
    svc = await central_state_registry.get_service(name)
    if not svc:
        raise HTTPException(404, f"Service {name} not found")
    return svc
