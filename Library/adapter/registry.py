"""
Adapter registry for AdapterManager.

- Register all adapter classes here for discovery and instantiation
"""

from typing import Dict, Type, Any

# Example: Placeholder for adapter classes (replace with real implementations)
class ExampleI2CAdapter:
    def __init__(self, config: Dict[str, Any]):
        pass

class ExampleCanbusAdapter:
    def __init__(self, config: Dict[str, Any]):
        pass

class ExampleKafkaAdapter:
    def __init__(self, config: Dict[str, Any]):
        pass

adapter_registry: Dict[str, Type] = {
    "i2c": ExampleI2CAdapter,
    "canbus": ExampleCanbusAdapter,
    "kafka": ExampleKafkaAdapter,
    # Add more adapters as needed
}
