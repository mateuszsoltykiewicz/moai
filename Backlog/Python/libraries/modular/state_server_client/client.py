import asyncio
import jsonschema
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from core.async_logging import setup_async_logger
from core.async_retry_helpers import async_retry

class StateServerClient:
    def __init__(self, kafka_servers, state_topic, group_id, schema, logger=None):
        self.kafka_servers = kafka_servers
        self.state_topic = state_topic
        self.group_id = group_id
        self.schema = schema
        self.logger = logger or setup_async_logger("state_server_client")
        self.producer = None
        self.consumer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_servers
        )
        self.consumer = AIOKafkaConsumer(
            self.state_topic,
            group_id=self.group_id,
            bootstrap_servers=self.kafka_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        )
        await self.producer.start()
        await self.consumer.start()

    @async_retry(max_attempts=5, delay=2)
    async def publish_state(self, state):
        jsonschema.validate(instance=state, schema=self.schema)
        await self.producer.send_and_wait(self.state_topic, state)
        self.logger.info(f"Published state with id {state.get('id')}")

    async def consume_states(self, callback):
        async for msg in self.consumer:
            try:
                jsonschema.validate(instance=msg.value, schema=self.schema)
                await callback(msg.value)
            except Exception as e:
                self.logger.error(f"Invalid state message: {e}")
