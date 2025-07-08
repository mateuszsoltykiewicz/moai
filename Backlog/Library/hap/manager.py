"""
Enhanced HAPManager with security, state sync, and production features.
"""

import asyncio
import threading
from typing import Dict, Any, Callable, List
from .schemas import HAPAccessoryConfig, HAPStatusResponse
from .exceptions import HAPError, HAPAccessoryError
from .metrics import record_hap_operation
from Library.logging import get_logger
from Library.mtls.manager import MtlsManager  # Security integration

# HAP-python imports
try:
    from pyhap.accessory_driver import AccessoryDriver
    from pyhap.accessory import Accessory
    from pyhap.bridge import Bridge
    from pyhap.const import CATEGORY_SENSOR
except ImportError:
    AccessoryDriver = None

logger = get_logger(__name__)

class HAPManager:
    def __init__(self, config: Dict[str, Any], component_factory: Callable, mtls_manager: MtlsManager):
        self._config = config
        self._accessories: Dict[str, Accessory] = {}
        self._driver: AccessoryDriver = None
        self._bridge: Bridge = None
        self._component_factory = component_factory
        self._lock = asyncio.Lock()
        self._mtls = mtls_manager
        self._running = False
        self._driver_thread: threading.Thread = None

    async def setup(self):
        """Secure setup with dependency checks"""
        if not AccessoryDriver:
            logger.critical("HAP-python library not installed")
            raise HAPError("HAP-python library not installed.")
        
        # Security: Verify mTLS is configured
        if not self._mtls.is_configured():
            logger.error("HAPManager requires mTLS configuration")
            raise HAPError("mTLS not configured")
        
        self._driver = AccessoryDriver(
            port=self._config.get("port", 51826),
            persist_file=self._config.get("persist_file", "homekit.state")
        )
        
        self._bridge = Bridge(
            self._driver,
            self._config.get("bridge_name", "AppLib Bridge")
        )
        
        # Create accessories with error handling
        for acc_cfg in self._config.get("accessories", []):
            try:
                component = self._component_factory(acc_cfg["component_name"])
                accessory = self._create_accessory(acc_cfg, component)
                self._bridge.add_accessory(accessory)
                self._accessories[acc_cfg["name"]] = accessory
                logger.info(f"Added accessory: {acc_cfg['name']}")
            except Exception as e:
                logger.error(f"Failed to create accessory {acc_cfg['name']}: {e}", exc_info=True)
                raise HAPAccessoryError(f"Accessory creation failed: {e}")
        
        self._driver.add_accessory(self._bridge)
        record_hap_operation("setup")
        logger.info("HAPManager setup complete")

    def _create_accessory(self, acc_cfg: dict, component: Any) -> Accessory:
        """Factory method with state synchronization"""
        class AppLibAccessory(Accessory):
            def __init__(self, driver, display_name):
                super().__init__(driver, display_name)
                self.component = component
                self.component_name = acc_cfg["component_name"]
                self.set_info_service(
                    firmware_revision="1.0",
                    manufacturer="AppLib",
                    model="Virtual",
                    serial_number="001"
                )
                
                # Dynamic service creation based on component type
                if acc_cfg["type"] == "sensor":
                    service = self.add_preload_service("TemperatureSensor")
                    self.char_temp = service.configure_char("CurrentTemperature")
                
                # State sync callback
                component.add_state_callback(self._update_state)
            
            def _update_state(self, new_state):
                """Sync component state to HomeKit"""
                if acc_cfg["type"] == "sensor":
                    self.char_temp.set_value(new_state["temperature"])
        
        return AppLibAccessory(self._driver, acc_cfg["name"])

    async def start(self):
        """Thread-safe driver start"""
        if not self._driver:
            raise HAPError("HAPManager not initialized")
        
        async with self._lock:
            if self._running:
                return
            
            # Start in dedicated thread
            self._driver_thread = threading.Thread(
                target=self._driver.start,
                daemon=True
            )
            self._driver_thread.start()
            self._running = True
            record_hap_operation("start")
            logger.info("HomeKit driver started")

    async def shutdown(self):
        """Graceful shutdown with thread management"""
        async with self._lock:
            if not self._running:
                return
            
            self._driver.stop()
            self._driver_thread.join(timeout=5.0)
            self._running = False
            record_hap_operation("shutdown")
            logger.info("HAPManager shutdown complete")

    async def get_status(self) -> HAPStatusResponse:
        """Status with accessory health checks"""
        accessory_status = []
        for name, acc in self._accessories.items():
            try:
                component = acc.component
                if hasattr(component, "health_check"):
                    status = await component.health_check()
                    accessory_status.append(f"{name}:{status}")
                else:
                    accessory_status.append(f"{name}:active")
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}", exc_info=True)
                accessory_status.append(f"{name}:error")
        
        return HAPStatusResponse(
            bridge_name=self._config.get("bridge_name", "AppLib Bridge"),
            accessories=accessory_status,
            running=self._running
        )
