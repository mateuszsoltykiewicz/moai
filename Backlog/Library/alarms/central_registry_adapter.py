import httpx
from .schemas import AlarmRaiseRequest, AlarmClearRequest

class CentralAlarmsAdapter:
    def __init__(self, registry_url: str):
        self._url = registry_url

    async def raise_alarm(self, req: AlarmRaiseRequest):
        async with httpx.AsyncClient() as client:
            await client.post(f"{self._url}/central_alarms/raise", json=req.dict())

    async def clear_alarm(self, req: AlarmClearRequest):
        async with httpx.AsyncClient() as client:
            await client.post(f"{self._url}/central_alarms/clear", json=req.dict())
