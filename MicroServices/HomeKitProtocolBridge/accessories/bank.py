from pyhap.accessory import Accessory
from pyhap.const import Category
import pyhap.loader as loader

class BankAccessory(Accessory):
    """HomeKit accessory for water bank (temperature, water presence, setpoint)."""

    category = Category.THERMOSTAT

    def __init__(self, *args, water_temp=20.0, water_present=True, setpoint=50.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.water_temp = water_temp
        self.water_present = water_present
        self.setpoint = setpoint
        self._setup_services()

    def _setup_services(self):
        thermostat = self.add_preload_service('Thermostat')
        self.char_current_temp = thermostat.get_characteristic('CurrentTemperature')
        self.char_target_temp = thermostat.get_characteristic('TargetTemperature')
        self.char_heating_cooling = thermostat.get_characteristic('TargetHeatingCoolingState')

        # Custom: Water presence as an occupancy sensor
        occ_service = self.add_preload_service('OccupancySensor')
        self.char_water_present = occ_service.get_characteristic('OccupancyDetected')

        self.update_from_backend(self.water_temp, self.water_present, self.setpoint)

    def update_from_backend(self, water_temp, water_present, setpoint):
        """Update accessory state from backend."""
        self.water_temp = water_temp
        self.water_present = water_present
        self.setpoint = setpoint
        self.char_current_temp.set_value(water_temp)
        self.char_target_temp.set_value(setpoint)
        # 0=Off, 1=Heat, 2=Cool, 3=Auto
        self.char_heating_cooling.set_value(1)
        self.char_water_present.set_value(1 if water_present else 0)
