"""
Kafka API Router (Advanced)

- Produce and consume messages with offset management and filtering
- Topic creation and configuration
- WebSocket streaming for real-time Kafka data
"""

from fastapi import APIRouter, Depends, status, Query, WebSocket, WebSocketDisconnect
from typing import Optional, List
from AppLib.models.schemas import (
    KafkaProduceRequest, KafkaProduceResponse,
    KafkaMessage, KafkaConsumeRequest, KafkaConsumeResponse,
    KafkaTopicCreateRequest, KafkaTopicCreateResponse
)
from api.dependencies import get_current_user
from api.main import APIException
from sessions.kafka import get_kafka_producer, get_kafka_consumer, get_admin_client
import json
import asyncio

router = APIRouter(tags=["kafka"])

@router.post(
    "/produce",
    response_model=KafkaProduceResponse,
    status_code=status.HTTP_200_OK,
    summary="Produce a Kafka message"
)
async def produce_kafka_message(
    req: KafkaProduceRequest,
    user=Depends(get_current_user)
):
    try:
        producer = await get_kafka_producer()
        value_bytes = json.dumps(req.value).encode("utf-8")
        key_bytes = req.key.encode("utf-8") if req.key else None
        kwargs = {}
        if req.partition is not None:
            kwargs["partition"] = req.partition
        await producer.send_and_wait(req.topic, value=value_bytes, key=key_bytes, **kwargs)
        return KafkaProduceResponse(success=True, message="Message produced.")
    except Exception as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to produce Kafka message.",
            details={"error": str(e)}
        )

@router.post(
    "/consume",
    response_model=KafkaConsumeResponse,
    summary="Consume Kafka messages (advanced)"
)
async def consume_kafka_messages(
    req: KafkaConsumeRequest,
    user=Depends(get_current_user)
):
    """
    Consume messages from a Kafka topic with advanced options.
    """
    try:
        group_id = req.group_id or f"api-kafka-consumer-{user['username']}"
        consumer = await get_kafka_consumer(
            req.topic, group_id,
            auto_commit=req.auto_commit,
            offset_reset=req.offset_reset
        )
        if req.partition is not None:
            tp = consumer.assignment().pop()
            tp = tp._replace(partition=req.partition)
            consumer.assign([tp])
        if req.offset is not None:
            partitions = consumer.assignment()
            for tp in partitions:
                consumer.seek(tp, req.offset)
        messages = []
        async for msg in consumer:
            messages.append(KafkaMessage(
                topic=msg.topic,
                key=msg.key.decode("utf-8") if msg.key else None,
                value=json.loads(msg.value),
                offset=msg.offset,
                partition=msg.partition,
                timestamp=msg.timestamp
            ))
            if len(messages) >= req.limit:
                break
        if not req.auto_commit:
            await consumer.commit()
        await consumer.stop()
        return KafkaConsumeResponse(messages=messages)
    except Exception as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to consume Kafka messages.",
            details={"error": str(e)}
        )

@router.post(
    "/topic/create",
    response_model=KafkaTopicCreateResponse,
    summary="Create Kafka topic"
)
async def create_kafka_topic(
    req: KafkaTopicCreateRequest,
    user=Depends(get_current_user)
):
    """
    Create a new Kafka topic with advanced config.
    """
    try:
        admin = get_admin_client()
        topic = NewTopic(
            req.topic,
            num_partitions=req.num_partitions,
            replication_factor=req.replication_factor,
            topic_configs=req.configs or {}
        )
        fs = admin.create_topics([topic])
        for topic, f in fs.items():
            f.result()  # Will raise exception on failure
        return KafkaTopicCreateResponse(success=True, message="Topic created")
    except Exception as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to create topic.",
            details={"error": str(e)}
        )

@router.post(
    "/topic/configure",
    response_model=KafkaTopicCreateResponse,
    summary="Update Kafka topic config"
)
async def update_kafka_topic_config(
    topic: str,
    configs: dict,
    user=Depends(get_current_user)
):
    """
    Update advanced Kafka topic configs.
    """
    try:
        admin = get_admin_client()
        from confluent_kafka.admin import ConfigResource, ConfigResourceType
        cfg_resource = ConfigResource(ConfigResourceType.TOPIC, topic, configs=configs)
        fs = admin.alter_configs([cfg_resource])
        for res, f in fs.items():
            f.result()
        return KafkaTopicCreateResponse(success=True, message="Topic config updated")
    except Exception as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to update topic config.",
            details={"error": str(e)}
        )

@router.websocket("/stream/{topic}")
async def kafka_stream_ws(
    websocket: WebSocket,
    topic: str,
    group_id: Optional[str] = None,
    limit: int = 100
):
    """
    WebSocket endpoint for real-time Kafka streaming.
    """
    await websocket.accept()
    try:
        consumer = await get_kafka_consumer(topic, group_id or "ws-stream", auto_commit=True)
        count = 0
        async for msg in consumer:
            await websocket.send_json({
                "topic": msg.topic,
                "key": msg.key.decode("utf-8") if msg.key else None,
                "value": json.loads(msg.value),
                "offset": msg.offset,
                "partition": msg.partition,
                "timestamp": msg.timestamp
            })
            count += 1
            if count >= limit:
                break
        await consumer.stop()
        await websocket.close()
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
