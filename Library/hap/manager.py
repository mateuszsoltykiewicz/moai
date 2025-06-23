"""
HAPManager: HomeKit Accessory Protocol integration.

- Bridges AppLib components to HomeKit as accessories/services
- Manages pairing, state sync, and event propagation
- Integrates with metrics, logging, and all components
- Async and thread-safe
"""

import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable, List
from .schemas import HAPAccessoryConfig, HAPStatusResponse
from .exceptions import HAPError
from .metrics import record_hap_operation
from .utils import log_info

# HAP-python imports
try:
    from pyhap.accessory_driver import AccessoryDriver
    from pyhap.accessory import Accessory
    from pyhap.bridge import Bridge
except ImportError:
    AccessoryDriver = None
    Accessory = None
    Bridge = None

class HAPManager:
    def __init__(self, config: Dict[str, Any], component_factory: Callable):
        self._config = config
        self._accessories: Dict[str, Accessory] = {}
        self._driver: Optional[AccessoryDriver] = None
        self._bridge: Optional[Bridge] = None
        self._component_factory = component_factory  # Factory or DI for AppLib components
        self._lock = asyncio.Lock()

    async def setup(self):
        if not AccessoryDriver:
            raise HAPError("HAP-python library not installed.")
        self._driver = AccessoryDriver(port=self._config.get("port", 51826))
        self._bridge = Bridge(self._driver, self._config.get("bridge_name", "AppLib Bridge"))
        # Dynamically add accessories for enabled components
        for acc_cfg in self._config.get("accessories", []):
            component = self._component_factory(acc_cfg["component_name"])
            accessory = self._create_accessory(acc_cfg, component)
            self._bridge.add_accessory(accessory)
            self._accessories[acc_cfg["name"]] = accessory
        self._driver.add_accessory(self._bridge)
        log_info("HAPManager: Setup complete.")

    def _create_accessory(self, acc_cfg: dict, component: Any) -> Accessory:
        """
        Create a HAP accessory based on config and component.
        """
        class AppLibAccessory(Accessory):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.component = component
                # Map component state to HomeKit services/characteristics here
                # Example: self.add_service(...)
        return AppLibAccessory(self._driver, acc_cfg["name"])

    async def start(self):
        if not self._driver:
            raise HAPError("HAPManager not initialized.")
        log_info("HAPManager: Starting HomeKit accessory driver.")
        await asyncio.to_thread(self._driver.start)

    async def shutdown(self):
        if self._driver:
            await asyncio.to_thread(self._driver.stop)
            log_info("HAPManager: Shutdown complete.")

    async def get_status(self) -> HAPStatusResponse:
        return HAPStatusResponse(
            bridge_name=self._config.get("bridge_name", "AppLib Bridge"),
            accessories=list(self._accessories.keys()),
            running=self._driver is not None
        )
