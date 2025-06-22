"""
Kafka API Router

- Configurable RBAC (via require_role)
- Pre/post hooks for validation/audit
- Default executions
- Comprehensive metrics and telemetry
- Structured logging
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from typing import Any, Dict, List
from models.schemas.kafka import (
    KafkaPublishRequest,
    KafkaPublishResponse,
    KafkaListMessagesResponse
)
from api.dependencies import base_endpoint_processor, require_role
from core.metrics import record_kafka_operation
from core.tracing import AsyncTracer
from core.logging import logger
from adapters.kafka import KafkaProducerAdapter, KafkaConsumerAdapter
import time
import json

tracer = AsyncTracer("applib-kafka").get_tracer()

router = APIRouter(
    prefix="/kafka",
    tags=["kafka"],
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"}
    }
)

@router.post(
    "/publish",
    response_model=KafkaPublishResponse,
    summary="Publish message to Kafka"
)
async def publish_message(
    req: KafkaPublishRequest = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="kafka:publish",
            pre_hook="api.hooks.kafka.before_publish",
            post_hook="api.hooks.kafka.after_publish",
            dependencies=[Depends(require_role("kafka.publish"))]
        )
    )
):
    """
    Publish message to Kafka.
    - RBAC via 'kafka.publish'
    - Pre/post hooks for validation/audit
    - Metrics and tracing
    """
    start_time = time.monotonic()
    try:
        # Pre-hook validation
        if "validation_result" in context and not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )
        with tracer.start_as_current_span("kafka_publish"):
            producer = KafkaProducerAdapter()
            key_bytes = req.key.encode("utf-8") if req.key else None
            value_bytes = json.dumps(req.value).encode("utf-8")
            await producer.publish(
                topic=req.topic,
                key=key_bytes,
                value=value_bytes
            )
            response = KafkaPublishResponse(
                success=True,
                message="Message published"
            )
        duration = time.monotonic() - start_time
        record_kafka_operation("publish", duration)
        logger.info(f"Message published to {req.topic} in {duration:.3f}s")
        return response
    except Exception as e:
        logger.error(f"Kafka publish failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish message: {str(e)}"
        )

@router.get(
    "/list/{topic}",
    response_model=KafkaListMessagesResponse,
    summary="List messages from Kafka topic"
)
async def list_messages(
    topic: str,
    limit: int = 10,
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="kafka:list",
            dependencies=[Depends(require_role("kafka.read"))]
        )
    )
):
    """
    List messages from Kafka topic.
    - RBAC via 'kafka.read'
    - Metrics and tracing
    """
    start_time = time.monotonic()
    try:
        with tracer.start_as_current_span("kafka_list"):
            consumer = KafkaConsumerAdapter(topic)
            messages = []
            async for msg in consumer:
                messages.append({
                    "key": msg.key.decode("utf-8") if msg.key else None,
                    "value": json.loads(msg.value),
                    "partition": msg.partition,
                    "offset": msg.offset,
                    "timestamp": msg.timestamp
                })
                if len(messages) >= limit:
                    break
            await consumer.stop()
            response = KafkaListMessagesResponse(messages=messages)
        duration = time.monotonic() - start_time
        record_kafka_operation("list", duration, count=len(messages))
        logger.info(f"Listed {len(messages)} messages from {topic} in {duration:.3f}s")
        return response
    except Exception as e:
        logger.error(f"Kafka list failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list messages: {str(e)}"
        )
