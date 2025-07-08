import asyncio
import sys
from typing import Literal
from Library.logging import get_logger
from Library.state import StateClient
from Library.alarms import AlarmClient
from Library.config import ConfigManager
from .hardware import I2CController
from .exceptions import CriticalHardwareError
from .metrics import record_command

logger = get_logger(__name__)

class I2CManager:
    _lock = asyncio.Lock()
    _state_client = StateClient(service_name="I2CAdapter")
    _alarm_client = AlarmClient()
    _controller = I2CController()
    _config = None

    @classmethod
    async def setup(cls):
        cls._config = await ConfigManager.get("I2CAdapter")
        await cls._state_client.setup()
        await cls._controller.initialize()
        await cls.clear_alarms_on_startup()
        logger.info("I2CManager setup complete")

    @classmethod
    async def shutdown(cls):
        await cls._controller.cleanup()
        await cls._state_client.shutdown()
        logger.info("I2CManager shutdown complete")

    @classmethod
    async def clear_alarms_on_startup(cls):
        await cls._alarm_client.clear_alarms(source="I2CAdapter")
        logger.info("Cleared I2CAdapter-specific alarms on startup")

    @classmethod
    async def execute_command(cls, command: Literal["PowerCutOff", "PowerOn", "HeatingStart", "HeatingStop"]):
        async with cls._lock:
            logger.info(f"Executing command: {command}")
            
            # Execute hardware command
            if command == "PowerCutOff":
                await cls._power_cut_off()
            elif command == "PowerOn":
                await cls._power_on()
            elif command == "HeatingStart":
                await cls._heating_start()
            elif command == "HeatingStop":
                await cls._heating_stop()
            else:
                raise ValueError(f"Invalid command: {command}")
            
            record_command(command)
            return f"Command {command} executed successfully"

    @classmethod
    async def _power_cut_off(cls):
        try:
            await cls._controller.trigger_power_cutoff()
            logger.warning("Power cut-off relay triggered")
            await cls._state_client.set("power_state", "off")
            await cls._alarm_client.raise_alarm(
                alarm_id="POWER_CUTOFF",
                message="Power cut-off activated",
                severity="FATAL"
            )
            logger.critical("FATAL alarm - stopping I2CAdapter")
            sys.exit(1)
        except CriticalHardwareError as e:
            logger.critical(f"Hardware failure during power cut-off: {e}")
            sys.exit(1)

    @classmethod
    async def _power_on(cls):
        await cls._controller.trigger_power_on()
        logger.info("Power on relay triggered")
        await cls._state_client.set("power_state", "on")

    @classmethod
    async def _heating_start(cls):
        await cls._controller.trigger_heating_start()
        logger.info("Heating start relay triggered")
        await cls._state_client.set("heating_state", "on")

    @classmethod
    async def _heating_stop(cls):
        await cls._controller.trigger_heating_stop()
        logger.info("Heating stop relay triggered")
        await cls._state_client.set("heating_state", "off")
