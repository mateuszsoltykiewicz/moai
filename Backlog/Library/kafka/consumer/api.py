from fastapi import APIRouter, HTTPException, Query, Depends, Request
from .manager import KafkaConsumerManager
from .schemas import KafkaConsumeResponse
from kafka.exceptions import KafkaError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/kafka/consumer", tags=["kafka_consumer"])

consumer_manager: KafkaConsumerManager = None

@router.get("/consume", response_model=list[KafkaConsumeResponse], dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "kafka_consumer", "read"))])
async def consume(
    topic: str = Query(...),
    group_id: str = Query("default-group"),
    limit: int = Query(10, ge=1, le=1000)
):
    try:
        return await consumer_manager.consume(topic, group_id, limit)
    except KafkaError as e:
        logger.error(f"Kafka consume error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=str(e))
