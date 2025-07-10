import asyncio
from functools import partial
from phew import json_response

# --- Sensors Controller ---
class SensorsController:
    """
    Handles heating logic, REST API, remote metrics polling, and disaster triggers.
    """
    def __init__(self, app, configuration):
        self._config = configuration
        self._app = app
        self.initialize = False

        self._apis = {
            f"{__name__.lower()}/initialize": (self.get_initialize, ["GET"]),
            f"{__name__.lower()}/initialize/<state>": (self.post_initialize, ["POST"]),
            f"{__name__.lower()}/metrics": (self.get_metrics, ["GET"])
        }
        self._api_setup()

    def _api_setup(self):
        """
        Register heating-related API endpoints.
        """
        for key, (func, methods) in self._apis.items():
            self._app.add_route(key, partial(func), methods=methods)
            self._config.registered_apis.append(key)

    async def temperature_reader(self):
        try:
            while True:
                asyncio.sleep(30)
        except asyncio.CancelledError:
            print("Shutting down temperature reader")
    
    async def water_available_reader(self):
        try:
            while True:
                asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Shutting down availability reader")
    
    async def flame_detector_reader(self):
        try:
            while True:
                asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Shutting down flame detection reader")
    
    async def gas_detector_reader(self):
        try:
            while True:
                asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Shutting down gas detection reader")
    

    async def get_initialize(self, request):
        """
        GET /initialize: Return initialization status.
        """
        return json_response({"initialized": self._config.initialized}, status=200)

    async def post_initialize(self, request, state):
        """
        POST /initialize/<state>: Engage or disengage initialization.
        """
        code = 200
        if state == "engage":
            self._config.initialized = True
        elif state == "disengage":
            self._config.initialized = False
        else:
            code = 400
        return json_response(status=code)

    
    async def get_metrics(self, request, filter):
        pass