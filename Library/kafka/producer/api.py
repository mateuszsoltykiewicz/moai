from fastapi import APIRouter, HTTPException, Body
from .manager import KafkaProducerManager
from .schemas import KafkaProduceRequest
from kafka.exceptions import KafkaError

router = APIRouter(prefix="/kafka/producer", tags=["kafka_producer"])

producer_manager: KafkaProducerManager = None

@router.post("/produce")
async def produce(req: KafkaProduceRequest = Body(...)):
    try:
        await producer_manager.produce(req)
        return {"success": True}
    except KafkaError as e:
        raise HTTPException(status_code=503, detail=str(e))
