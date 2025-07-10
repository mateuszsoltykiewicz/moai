import uasyncio
from functools import partial
from phew import json_response

# --- Shared Configuration Class ---
class Configuration:
    """
    Central configuration/state object for all controllers.
    Holds hardware state, API registration, and disaster flags.
    """
    def __init__(self, app, wlan, connection_timeout=10, api_readiness_timeout=20):
        self.disaster_detected = False
        self.watchdog_time = None
        self.initialized = False
        self.disaster_reason = []
        self.should_shutdown = False
        self.shutdown_ready = False
        self.exit_code = 0
        self.api_ready = False
        self.wlan = wlan
        self.connection_timeout = connection_timeout
        self._api_readiness_timeout = api_readiness_timeout
        self.registered_apis = []
        self._required_apis = [
            "relaysconfiguration/configuration",
            "heatingcontroller/heating",
            "heatingcontroller/initialize",
            "heatingcontroller/health",
            "shutdowncontroller/shutdown"
        ]
        self._app = app
        self._apis = {
            f"{__name__.lower()}/configuration": (self.get_configuration, ["GET"])
        }
        self._apis_setup()

    def _apis_setup(self):
        """
        Register configuration-related API endpoints.
        """
        for key, (func, methods) in self._apis.items():
            self._app.add_route(key, partial(func), methods=methods)
            self.registered_apis.append(key)

    async def get_configuration(self, request):
        """
        API endpoint: Return current configuration (excluding non-serializable objects).
        """
        result = {k: v for k, v in self.__dict__.items()
                  if not callable(v) and not k.startswith('_')}
        return json_response(result, status=200)

    async def validate_apis(self):
        """
        Periodically check that all required APIs are registered.
        If not, trigger a disaster.
        """
        try:
            while not self.api_ready and self._api_readiness_timeout > 0:
                await asyncio.sleep(1)
                self._api_readiness_timeout -= 1
                missing_apis = [api for api in self._required_apis if api not in self.registered_apis]
                if missing_apis:
                    self.api_ready = False
                    self.disaster_detected = True
                    self.disaster_reason.append("APIs readiness check has failed!")
                    return False, missing_apis
            self.api_ready = True
            return True, []
        except asyncio.CancelledError:
            pass
