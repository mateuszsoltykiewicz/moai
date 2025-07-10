import asyncio
from functools import partial
from phew import json_response
from utime import time
import urequests

# --- Heating Controller ---
class HeatingController:
    """
    Handles heating logic, REST API, remote metrics polling, and disaster triggers.
    """
    def __init__(self, app, configuration):
        self._config = configuration
        self._app = app
        self._apis = {
            f"{__name__.lower()}/heating/<state>": (self.post_heating, ["POST"]),
            f"{__name__.lower()}/heating": (self.get_heating, ["GET"]),
            f"{__name__.lower()}/initialize": (self.get_initialize, ["GET"]),
            f"{__name__.lower()}/initialize/<state>": (self.post_initialize, ["POST"])
        }
        self._api_setup()

    def _api_setup(self):
        """
        Register heating-related API endpoints.
        """
        for key, (func, methods) in self._apis.items():
            self._app.add_route(key, partial(func), methods=methods)
            self._config.registered_apis.append(key)

    async def post_heating(self, request, state):
        """
        POST /heating/<state>: Engage or disengage heating.
        """
        code = 200
        if state == "engage":
            self._config.is_heating = True
        elif state == "disengage":
            self._config.is_heating = False
        else:
            code = 400
        return json_response(status=code)

    async def get_heating(self, request):
        """
        GET /heating: Return heating status.
        """
        return json_response({"status": self._config.is_heating}, status=200)

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

    async def heating_on(self):
        """
        Async task: Engage heating hardware sequence.
        """
        try:
            while True:
                await asyncio.sleep(1)
                if self._config.initialized and self._config.is_heating and not self._config.heating_engaged:
                    self._config.gas_valve.on()
                    self._config.spark.on()
                    await asyncio.sleep(2)
                    self._config.spark.off()
                    self._config.heating_engaged = True
        except asyncio.CancelledError:
            print("Shutting down heating_on")

    async def heating_off(self):
        """
        Async task: Disengage heating hardware sequence.
        """
        try:
            while True:
                await asyncio.sleep(1)
                if not self._config.is_heating and not self._config.disaster_detected:
                    if self._config.gas_valve.value() or self._config.spark.value():
                        self._config.gas_valve.off()
                        self._config.spark.off()
                        self._config.heating_engaged = False
        except asyncio.CancelledError:
            print("Shutting down heating_off")

    async def initialized(self):
        """
        Async task: Engage/disengage pump based on initialization state.
        """
        try:
            while True:
                await asyncio.sleep(1)
                if self._config.initialized:
                    self._config.pump.on()
                else:
                    self._config.pump.off()
        except asyncio.CancelledError:
            print("Shutting down initialized")

    async def heating_monitor(self):
        """
        Async task: Monitor temperature change during heating.
        Trigger disaster if temperature does not rise as expected.
        """
        try:
            while True:
                await asyncio.sleep(1)
                while self._config.is_heating:
                    self._config.last_temperature = self._config.current_temperature
                    await asyncio.sleep(self._config.delta_temp_timeout)
                    if self._config.last_temperature + self._config.expected_delta_temp < self._config.current_temperature:
                        self._config.is_heating = False
                        self._config.disaster_detected = True
                        self._config.disaster_reason.append("Temperature hasn't changed within timeout period!")
        except asyncio.CancelledError:
            print("Shutting down heating_monitor")

    async def shutdown_task(self):
        """
        Safely turn off all hardware relays.
        """
        self._config.pump.off()
        self._config.gas_valve.off()
        self._config.spark.off()

    async def fetch_remote_metrics(self):
        """
        Periodically fetch remote sensor metrics via REST API.
        Trigger disaster if connection is lost (only if initialized).
        """
        try:
            while True:
                await asyncio.sleep(self._config.metrics_poll_interval)
                if not self._config.initialized:
                    continue  # Only fetch if initialized
                try:
                    response = urequests.get(self._config.metrics_poll_url)
                    if response.status_code == 200:
                        data = response.json()
                        self._config.current_temperature = data.get("temperature", self._config.current_temperature)
                        self._config.water_available = data.get("water_available", self._config.water_available)
                        self._config.gas_leak = data.get("gas_leak", self._config.gas_leak)
                        self._config.metrics_last_update = time()
                    else:
                        raise Exception("Non-200 response")
                except Exception as e:
                    print(f"Failed to fetch remote metrics: {e}")
                    if self._config.initialized:  # Only trigger disaster if initialized
                        self._config.disaster_detected = True
                        self._config.disaster_reason.append("Lost connection to remote sensor API")
        except asyncio.CancelledError:
            print("Shutting down fetch_remote_metrics")

    async def metrics_update_watchdog(self):
        """
        Monitor the freshness of remote metrics.
        Trigger disaster if metrics are stale.
        """
        try:
            while True:
                await asyncio.sleep(self._config.metrics_poll_interval)
                if self._config.metrics_last_update is None:
                    continue  # Not yet updated
                elapsed = time() - self._config.metrics_last_update
                if elapsed > self._config.metrics_poll_timeout:
                    print(f"Metrics watchdog failed: {elapsed} seconds ago.")
                    if self._config.initialized:
                        self._config.disaster_detected = True
                        self._config.disaster_reason.append("Metrics watchdog timeout")
        except asyncio.CancelledError:
            print("Shutting down metrics_update_watchdog")

    async def metrics_analyzer(self):
        """
        Analyze fetched metrics for critical conditions.
        Trigger disaster on water/gas anomalies.
        """
        try:
            while True:
                await asyncio.sleep(1)
                if self._config.initialized:
                    if not self._config.water_available:
                        self._config.disaster_detected = True
                        self._config.disaster_reason.append("Water tank empty!")
                    if self._config.gas_leak:
                        self._config.disaster_detected = True
                        self._config.disaster_reason.append("Gas leak detected!")
        except asyncio.CancelledError:
            print("Shutting down metrics_analyzer")
