import network
from phew import server, json_response
import machine
from utime import time
import uasyncio as asyncio
from functools import partial

PUMP_PIN = 1
GAS_VALVE_PIN = 2
SPARK_PIN = 3

pump = machine.Pin(PUMP_PIN, machine.Pin.OUT)
gas_valve = machine.Pin(GAS_VALVE_PIN, machine.Pin.OUT)
spark = machine.Pin(SPARK_PIN, machine.Pin.OUT)

class Configuration:
    def __init__(self):
        self.is_heating = False
        self.heating_engaged = False
        self.disaster_detected = False
        self.watchdog_time = None
        self.initialized = False
        self.disaster_reason = []

class HeatingController:
    def __init__(self, configuration: Configuration):
        self.config = configuration
    
    async def heating_on(self):
        while True:
            await asyncio.sleep(1)
            if self.config.initialized and self.config.is_heating and not self.config.heating_engaged:
                # Implement relay logic here
                self.config.heating_engaged = True

    async def heating_off(self):
        while True:
            await asyncio.sleep(1)
            if self.config.initialized and not self.config.is_heating:
                self.config.heating_engaged = False

class DisasterController:
    def __init__(self, configuration: Configuration):
        self.config = configuration
    
    async def disaster_monitor(self):
        while not self.config.disaster_detected:
            await asyncio.sleep(1)
        reason = "\n".join(self.config.disaster_reason) if self.config.disaster_reason else "Disaster detected!"
        raise Exception(reason)

class WatchdogTimer:
    def __init__(self, countdown_seconds: int, watchdog_period_seconds: int, configuration: Configuration):
        self._countdown_seconds = countdown_seconds
        self._watchdog_period_seconds = watchdog_period_seconds
        self.config = configuration

    async def countdown(self):
        while True:
            while self.config.initialized:
                await asyncio.sleep(self._countdown_seconds)
                if self.config.watchdog_time is None:
                    print("No status logged yet.")
                    continue
                elapsed = time() - self.config.watchdog_time
                if elapsed > self._watchdog_period_seconds:
                    print(f"Status is outside watchdog period: {elapsed} seconds ago.")
                    self.config.disaster_detected = True
                    self.config.disaster_reason.append("Watchdog timeout")

class NetworkConnection:
    def __init__(self, network_name: str = None, network_pass: str = None, countdown: int = 10, configuration: Configuration = None):
        self._network_name = network_name
        self._network_pass = network_pass
        self._network_status = False
        self._network_config = None
        self._countdown = countdown
        self.config = configuration
    
    async def network_connect(self) -> bool:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self._network_name, self._network_pass)

        while not wlan.isconnected() and self._countdown >= 0:
            await asyncio.sleep(1)
            self._countdown -= 1

        if wlan.isconnected():
            print("Network connection successful")
        else:
            print("Network connection failed!")
            if self.config:
                self.config.disaster_detected = True

class Apis:
    @staticmethod
    async def pump_control(request, state, config: Configuration):
        if state == "on":
            pump.on()
            return json_response({"status": "Pump ON"})
        elif state == "off":
            pump.off()
            return json_response({"status": "Pump OFF"})
        else:
            return json_response({"error": "Invalid state"}, status=400)

    @staticmethod
    async def heating_control(request, state, config: Configuration):
        if state == "on":
            config.is_heating = True
            return json_response({"status": "Heating ON"})
        elif state == "off":
            config.is_heating = False
            return json_response({"status": "Heating OFF"})
        else:
            return json_response({"error": "Invalid state"}, status=400)

    @staticmethod
    async def health(request, config: Configuration):
        config.watchdog_time = time()
        return json_response(200)

    @staticmethod
    async def initialize(request, state, config: Configuration):
        code = 200
        if state == "enable":
            config.initialized = True
        elif state == "disable":
            config.initialized = False
        else:
            code = 500
        return json_response(code)

    @staticmethod
    async def status(request, config: Configuration):
        return json_response({"status": config.is_heating})

async def main(app):
    # Use functools.partial to inject config into API handlers
    app.add_route("/health", partial(Apis.health, 
                                     config=configuration), 
                                     methods=["GET"])
    app.add_route("/pump/<state>", partial(Apis.pump_control, 
                                           config=configuration), 
                                           methods=["POST"])
    app.add_route("/status/<state>", partial(Apis.heating_control, 
                                             config=configuration), 
                                             methods=["POST"])
    app.add_route("/status", partial(Apis.status, 
                                     config=configuration), 
                                     methods=["GET"])
    app.add_route("/initialize/<state>", partial(Apis.initialize, 
                                                 config=configuration), 
                                                 methods=["POST"])

    configuration = Configuration()

    disaster_controller = DisasterController(configuration)
    asyncio.create_task(disaster_controller.disaster_monitor())
    
    network_connection = NetworkConnection(network_name="GdzieMojSwiatlowodWrr", 
                                           network_pass="nivvud-vyfbon-jafkI0",
                                           configuration=configuration)
    await network_connection.network_connect()

    watchdog = WatchdogTimer(countdown_seconds=10,
                             watchdog_period_seconds=15,
                             configuration=configuration)
    asyncio.create_task(watchdog.countdown())

    heating = HeatingController(configuration)
    asyncio.create_task(heating.heating_on())
    asyncio.create_task(heating.heating_off())

app = server.Phew()
asyncio.run(main(app=app))
