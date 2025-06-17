"""
Domain events for AppLib Core.

Events are plain objects that represent significant business occurrences.
Handlers (optional) can be registered to react to these events.
"""

from datetime import datetime
from typing import Callable, Dict, List, Type, Any

# --- Event Definitions ---

class DeviceActivated:
    def __init__(self, device_id: str, activated_at: datetime):
        self.device_id = device_id
        self.activated_at = activated_at

class DeviceDeactivated:
    def __init__(self, device_id: str, deactivated_at: datetime):
        self.device_id = device_id
        self.deactivated_at = deactivated_at

class UserDeactivated:
    def __init__(self, user_id: str, deactivated_at: datetime):
        self.user_id = user_id
        self.deactivated_at = deactivated_at

# --- Simple Event Dispatcher (Optional) ---

class EventDispatcher:
    """
    Simple in-memory event dispatcher for synchronous event handling.
    """
    def __init__(self):
        self._handlers: Dict[Type, List[Callable[[Any], None]]] = {}

    def register(self, event_type: Type, handler: Callable[[Any], None]):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def dispatch(self, event: Any):
        for handler in self._handlers.get(type(event), []):
            handler(event)

# Example usage (in tests or main app logic):
# dispatcher = EventDispatcher()
# dispatcher.register(DeviceActivated, lambda e: print(f"Device {e.device_id} activated at {e.activated_at}"))
# dispatcher.dispatch(DeviceActivated(device_id="dev123", activated_at=datetime.utcnow()))
