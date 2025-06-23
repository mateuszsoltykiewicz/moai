"""
API endpoints for AdapterManager.

- Exposes /adapter/ for adapter management and discovery
"""

from fastapi import APIRouter, HTTPException, Body
from .manager import AdapterManager
from .schemas import AdapterInfo, AdapterConfig
from .exceptions import AdapterNotFoundError

router = APIRouter(prefix="/adapter", tags=["adapter"])

adapter_manager = AdapterManager()

@router.post("/", response_model=AdapterInfo)
async def create_adapter(req: AdapterConfig = Body(...)):
    """
    Create or retrieve an adapter instance by type and config.
    """
    try:
        adapter = await adapter_manager.get_adapter(req.type, req.config)
        return {"type": req.type, "class_name": adapter.__class__.__name__}
    except AdapterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=Dict[str, str])
async def list_adapters():
    """
    List all registered adapter types.
    """
    return await adapter_manager.list_adapters()
