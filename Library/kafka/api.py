"""
API endpoints for KafkaManager.

- Exposes /kafka/produce and /kafka/consume endpoints
"""

from fastapi import APIRouter, HTTPException, Body, Query
from .manager import KafkaManager
from .schemas import KafkaProduceRequest, KafkaConsumeResponse
from .exceptions import KafkaError

router = APIRouter(prefix="/kafka", tags=["kafka"])

# kafka_manager should be initialized with config at app startup
kafka_manager: KafkaManager = None

@router.post("/produce")
async def produce(req: KafkaProduceRequest = Body(...)):
    """
    Produce a message to a Kafka topic.
    """
    try:
        await kafka_manager.produce(req)
        return {"success": True}
    except KafkaError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/consume", response_model=list[KafkaConsumeResponse])
async def consume(
    topic: str = Query(...),
    group_id: str = Query("default"),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Consume messages from a Kafka topic.
    """
    try:
        return await kafka_manager.consume(topic, group_id, limit)
    except KafkaError as e:
        raise HTTPException(status_code=503, detail=str(e))
