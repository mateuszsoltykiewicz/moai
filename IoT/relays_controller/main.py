import network
from phew import server, json_response
import machine
from utime import time
import uasyncio as asyncio

PUMP_PIN: int = 1

GAS_VALVE_PIN: int = 2
SPARK_PIN: int = 3

pump = machine.Pin(PUMP_PIN, machine.Pin.OUT)
gas_valve = machine.Pin(GAS_VALVE_PIN, machine.Pin.OUT)
spark = machine.Pin(SPARK_PIN, machine.Pin.OUT)

is_heating: bool = False
heating_engaged: bool = False
disaster_detected: bool = False
watchdog = None
initialized: bool = False
disaster_reason: list[str] = []

class HeatingController:
    def __init__(self):
        pass
    
    async def heating_on(self):
      while True:
          global initialized
          while initialized:
              global heating_engaged
              if is_heating and not heating_engaged:
                pass
    
    async def heating_off(self):
        while True:
            global initialized
            while initialized:
                if not is_heating:
                    global heating_engaged
                    heating_engaged = False
    
class DisasterController:

    @staticmethod
    async def disaster_monitor() -> None:
        global disaster_detected
        while not disaster_detected:
            await asyncio.sleep(1)
        global disaster_reason
        raise Exception(f"{'\n'.join(disaster_reason)}")

class WatchdogTimer:
    def __init__(self, countdown_seconds, watchdog_period_seconds):
        self.countdown_seconds = countdown_seconds
        self.watchdog_period_seconds = watchdog_period_seconds
        self.last_status_time = None

    async def countdown(self):
      while True:
        global initialized
        while initialized:
          # Asynchronous countdown
          await asyncio.sleep(self.countdown_seconds)
          # After countdown, check last status
          global watchdog
          if watchdog is None:
              print("No status logged yet.")
              return False
          elapsed = time() - watchdog
          if elapsed <= self.watchdog_period_seconds:
              print(f"Status is within watchdog period: {elapsed} seconds ago.")
          else:
              print(f"Status is outside watchdog period: {elapsed} seconds ago.")
              global disaster_detected
              disaster_detected = True
            
class NetworkConnection:
    def __init__(self, network_name: str = None, network_pass: str = None, countdown: int = 10):
        self._network_name: str = network_name
        self._network_pass: str = network_pass
        self._network_status: bool = False
        self._network_config = None
        self._countdown: int = countdown
    
    async def network_connect(self) -> bool:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self._network_name, self._network_pass)
        while not wlan.isconnected() or self._countdown >= 0:
            await asyncio.sleep(1)
            self._countdown -= 1

        if wlan.isconnected():
            print("Network connection succesful")
        else:
            print("Network connection failed!")
            global disaster_detected
            disaster_detected = True
            
class Apis:

    @staticmethod
    async def pump_control(request, state):
        if state == "on":
            pump.on()
            return json_response({"status": "Pump ON"})
        elif state == "off":
            pump.off()
            return json_response({"status": "Pump OFF"})
        else:
            return json_response({"error": "Invalid state"}, status=400)

    @staticmethod
    async def heating_control(request, state):
        if state == "on":
            pump.on()
            global is_heating
            is_heating = True
            return json_response({"status": "Heating ON"})
        elif state == "off":
            pump.off()
            global is_heating
            is_heating = False
            return json_response({"status": "Heating OFF"})
        else:
            return json_response({"error": "Invalid state"}, status=400)

    @staticmethod
    async def health(request):
        global watchdog
        watchdog = time()
        return json_response(200)
    
    @staticmethod
    async def initialize(request, state):
        global initialized
        initialized = state
        return json_response(200)
    
    @staticmethod
    async def status(request):
        return json_response({"status": True}) if is_heating else json_response({"status", False})

async def main(app): 
    disaster_controller = DisasterController()
    asyncio.create_task(disaster_controller.disaster_monitor())
    
    network_connection = NetworkConnection(network_name="GdzieMojSwiatlowodWrr", network_pass="nivvud-vyfbon-jafkI0")
    await network_connection.network_connect()

    app.add_route("/health", Apis.status, methods=["GET"])
    app.add_route("/pump/<state>", Apis.pump_control, methods=["POST"])
    app.add_route("/status/<state>", Apis.heating_control, methods=["POST"])
    app.add_route("/status", Apis.heating, methods=["GET"])
    app.add_route("initialize/<state>", Apis.initialize, methods=["POST"])

    watchdog = WatchdogTimer(countdown_seconds=10, watchdog_period_seconds=15)
    asyncio.create_task(watchdog.countdown())

    heating = HeatingController()
    asyncio.create_task(heating.heating_on())
    asyncio.create_task(heating.heating_off())

app = server.Phew()
asyncio.run(main(app=app))
