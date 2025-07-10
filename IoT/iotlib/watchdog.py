import asyncio
from functools import partial
from phew import json_response
from utime import time

# --- Watchdog Controller ---
class WatchdogController:
    """
    Monitors system health via a heartbeat endpoint.
    """
    def __init__(self, app, configuration, countdown_seconds=25, watchdog_period_seconds=20):
        self._countdown_seconds = countdown_seconds
        self._watchdog_period_seconds = watchdog_period_seconds
        self._config = configuration
        self._app = app
        self._apis = {f"{__name__.lower()}/health": (self.health, ["GET"])}
        self._apis_setup()

    def _apis_setup(self):
        for key, (func, methods) in self._apis.items():
            self._app.add_route(key, partial(func), methods=methods)
            self._config.registered_apis.append(key)

    async def health(self, request):
        """
        GET /health: Heartbeat endpoint to reset watchdog timer.
        """
        self._config.watchdog_time = time()
        return json_response(status=200)

    async def watchdog_timeout(self):
        """
        Async task: Monitor for missed heartbeats and trigger disaster.
        """
        try:
            while True:
                await asyncio.sleep(1)
                while self._config.initialized:
                    await asyncio.sleep(self._countdown_seconds)
                    if self._config.watchdog_time is None:
                        continue
                    elapsed = time() - self._config.watchdog_time
                    if elapsed > self._watchdog_period_seconds:
                        print(f"Status is outside watchdog period: {elapsed} seconds ago.")
                        self._config.disaster_detected = True
                        self._config.disaster_reason.append("Watchdog timeout")
        except asyncio.CancelledError:
            print("Shutting down watchdog_timeout")
