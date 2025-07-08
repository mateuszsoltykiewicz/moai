"""
Adapter registry for AdapterManager.

- Registers all available manager classes as adapters for dynamic discovery and instantiation.
"""

from Library.i2c.manager import I2CManager
from Library.kafka.manager import KafkaProducerManager, KafkaConsumerManager
from Library.database.manager import DatabaseManager
from Library.canbus.manager import CanbusManager
# Import other managers as needed

adapter_registry = {
    "i2c": I2CManager,
    "kafka_producer": KafkaProducerManager,
    "kafka_consumer": KafkaConsumerManager,
    "database": DatabaseManager,
    "canbus": CanbusManager,
    # Add more adapters as needed
}
