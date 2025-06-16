from pyhap.accessory_driver import AccessoryDriver
from pyhap.accessory import Bridge
import pyhap.loader as loader
import asyncio

class HomeKitAdapter:
    def __init__(self, config_path):
        self.config_path = config_path
        self.driver = None
        self.bridge = None
        self.accessories = {}

    def start(self):
        self.driver = AccessoryDriver(port=51826, persist_file=self.config_path)
        self.bridge = Bridge(self.driver, 'My HomeKit Bridge')
        self.driver.add_accessory(accessory=self.bridge)
        asyncio.create_task(self.driver.start())

    def add_accessory(self, name, category, services):
        # Dynamically create accessory instance
        acc = self._create_accessory(name, category, services)
        self.bridge.add_accessory(acc)
        self.accessories[name] = acc
        self.driver.config_changed()  # Notify HomeKit of config change[11]

    def remove_accessory(self, name):
        acc = self.accessories.pop(name, None)
        if acc:
            self.bridge.accessories.pop(acc.aid, None)
            self.driver.config_changed()

    def _create_accessory(self, name, category, services):
        # Example: create a lightbulb accessory
        from pyhap.accessory import Accessory
        acc = Accessory(self.driver, name)
        for service_name in services:
            acc.add_preload_service(service_name)
        return acc
