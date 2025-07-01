from pyhap.accessory import Accessory
from pyhap.const import Category
import pyhap.loader as loader

class AlarmsAccessory(Accessory):
    """HomeKit accessory representing platform alarms."""

    category = Category.SECURITY_SYSTEM

    def __init__(self, *args, alarms=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.alarms = alarms or []
        self._setup_services()

    def _setup_services(self):
        # SecuritySystem service shows alarm state
        sec_sys = self.add_preload_service('SecuritySystem')
        self.char_current_state = sec_sys.get_characteristic('SecuritySystemCurrentState')
        self.char_alarm_count = sec_sys.configure_char(
            'StatusFault', value=0, properties={'Format': 'uint8', 'minValue': 0, 'maxValue': 255}
        )

        # Custom: List of critical/FATAL alarms as a read-only characteristic (string)
        self.char_critical_list = sec_sys.configure_char(
            'StatusActive', value="", properties={'Format': 'string'}
        )

        self.update_from_backend(self.alarms)

    def update_from_backend(self, alarms):
        """Update accessory state from backend alarms list."""
        self.alarms = alarms
        num_active = len([a for a in alarms if a.get("active", True)])
        self.char_alarm_count.set_value(num_active)
        # FATAL first, then critical, then others
        sorted_alarms = sorted(
            [a for a in alarms if a.get("severity") in ("FATAL", "CRITICAL", "ERROR")],
            key=lambda a: {"FATAL": 0, "CRITICAL": 1, "ERROR": 2}.get(a.get("severity"), 99)
        )
        critical_list = "; ".join(f"{a['severity']}: {a['message']}" for a in sorted_alarms)
        self.char_critical_list.set_value(critical_list[:255])  # HomeKit string length limit
        # Set HomeKit state: 0=Disarmed, 1=ArmedAway, 2=ArmedHome, 3=ArmedNight, 4=Triggered
        self.char_current_state.set_value(4 if any(a['severity'] == "FATAL" for a in alarms) else 1)
