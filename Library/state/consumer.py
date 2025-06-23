# central_state/consumer.py

from .manager import CentralStateRegistry

async def consume_state_events(kafka_manager, central_state_registry):
    while True:
        messages = await kafka_manager.consume("state_events", group_id="central_state")
        for msg in messages:
            service_name = msg.key
            state = msg.value
            await central_state_registry.register_or_update(
                service_name=service_name,
                state=state
            )
