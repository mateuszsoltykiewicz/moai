from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/config/reload")
async def reload_config(config_service: ConfigService = Depends(get_config_service)):
    await config_service.reload()
    return {"status": "reloaded"}
