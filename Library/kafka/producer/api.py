from fastapi import APIRouter, HTTPException, Body, Depends, Request
from .manager import KafkaProducerManager
from .schemas import KafkaProduceRequest
from kafka.exceptions import KafkaError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/kafka/producer", tags=["kafka_producer"])

producer_manager: KafkaProducerManager = None

@router.post("/produce", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "kafka_producer", "write"))])
async def produce(req: KafkaProduceRequest = Body(...)):
    try:
        await producer_manager.produce(req)
        return {"success": True}
    except KafkaError as e:
        logger.error(f"Kafka produce error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=str(e))
