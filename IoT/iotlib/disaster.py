from uasyncio import asyncio

# --- Disaster Controller ---
class DisasterController:
    """
    Monitors for disaster conditions and coordinates shutdown.
    """
    def __init__(self, configuration):
        self._config = configuration

    async def disaster_monitor(self):
        """
        Async task: Wait for disaster, then trigger shutdown.
        """
        while not self._config.disaster_detected:
            await asyncio.sleep(1)
        self._config.should_shutdown = True
        countdown = 20
        while not self._config.shutdown_ready and countdown > 0:
            await asyncio.sleep(1)
            countdown -= 1
        if countdown == 0:
            self._config.disaster_reason.append("Graceful shutdown failed!")
            raise Exception("\n".join(self._config.disaster_reason))
