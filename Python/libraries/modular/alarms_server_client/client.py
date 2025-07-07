from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from core.async_logging import setup_async_logger
from core.async_retry_helpers import async_retry

class AlarmsServerClient:
    def __init__(self, kafka_servers, alarm_topic, group_id, schema, logger=None):
        self.kafka_servers = kafka_servers
        self.alarm_topic = alarm_topic
        self.group_id = group_id
        self.schema = schema
        self.logger = logger or setup_async_logger("alarms_server_client")
        self.producer = None
        self.consumer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_servers
        )
        self.consumer = AIOKafkaConsumer(
            self.alarm_topic,
            group_id=self.group_id,
            bootstrap_servers=self.kafka_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        )
        await self.producer.start()
        await self.consumer.start()

    @async_retry(max_attempts=5, delay=2)
    async def publish_alarm(self, alarm_event):
        jsonschema.validate(instance=alarm_event, schema=self.schema)
        await self.producer.send_and_wait(self.alarm_topic, alarm_event)
        self.logger.info(f"Published alarm event: {alarm_event.get('type')}")

    async def consume_alarms(self, callback):
        async for msg in self.consumer:
            try:
                jsonschema.validate(instance=msg.value, schema=self.schema)
                await callback(msg.value)
            except Exception as e:
                self.logger.error(f"Invalid alarm message: {e}")
