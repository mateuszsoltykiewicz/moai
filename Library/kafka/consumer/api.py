from fastapi import APIRouter, HTTPException, Query
from .manager import KafkaConsumerManager
from .schemas import KafkaConsumeResponse
from kafka.exceptions import KafkaError

router = APIRouter(prefix="/kafka/consumer", tags=["kafka_consumer"])

consumer_manager: KafkaConsumerManager = None

@router.get("/consume", response_model=list[KafkaConsumeResponse])
async def consume(
    topic: str = Query(...),
    group_id: str = Query("default-group"),
    limit: int = Query(10, ge=1, le=1000)
):
    try:
        return await consumer_manager.consume(topic, group_id, limit)
    except KafkaError as e:
        raise HTTPException(status_code=503, detail=str(e))
