from pyhap.accessory import Accessory
from pyhap.const import Category
import pyhap.loader as loader

class HeatingAccessory(Accessory):
    """HomeKit accessory for heating control and status."""

    category = Category.THERMOSTAT

    def __init__(self, *args, status="off", **kwargs):
        super().__init__(*args, **kwargs)
        self.status = status
        self._setup_services()

    def _setup_services(self):
        # Use HeaterCooler service for heating control
        heater = self.add_preload_service('HeaterCooler')
        self.char_active = heater.get_characteristic('Active')
        self.char_current_state = heater.get_characteristic('CurrentHeaterCoolerState')
        self.char_target_state = heater.get_characteristic('TargetHeaterCoolerState')

        # Set initial state
        self.update_from_backend(self.status)

    def update_from_backend(self, status):
        """Update accessory state from backend."""
        self.status = status
        # 0=Inactive, 1=Active
        self.char_active.set_value(1 if status == "running" else 0)
        # 0=Inactive, 1=Idle, 2=Heating
        self.char_current_state.set_value(2 if status == "running" else 0)
        # 0=Auto, 1=Heat, 2=Cool (use Heat for heating)
        self.char_target_state.set_value(1)
