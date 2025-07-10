from uasyncio import asyncio
from functools import partial


# --- Shutdown Controller ---
class ShutdownController:
    """
    Handles graceful shutdown of all async tasks and hardware.
    """
    def __init__(self, app, config, tasks, shutdown_task):
        self._config = config
        self._tasks = tasks
        self._shutdown_task = shutdown_task
        self._apis = {f"{__name__.lower()}/shutdown": (self.shutdown, ["POST"])}
        self._app = app
        self._api_setup()

    def _api_setup(self):
        for key, (func, methods) in self._apis.items():
            self._app.add_route(key, partial(func), methods=methods)
            self._config.registered_apis.append(key)

    async def shutdown(self, request):
        """
        POST /shutdown: Trigger system shutdown.
        """
        self._config.should_shutdown = True

    async def should_shutdown(self):
        """
        Async task: Wait for shutdown trigger, then cancel all tasks and cleanup.
        """
        while not self._config.should_shutdown:
            await asyncio.sleep(1)
        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
        await self._shutdown_task()
        self._config.shutdown_ready = True
        self._config.exit_code = 0
