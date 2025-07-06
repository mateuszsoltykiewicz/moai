import uasyncio as asyncio
from machine import Pin
import time
from iotlib import (
    NetworkManager, AuthManager, ConfigManager, WatchdogManager, StateManager,
    Logger, TimeSyncManager, AlarmManager, OTAUpdateManager
)

# --- REST API for Relay Control (simplified example) ---
try:
    import picoweb
except ImportError:
    picoweb = None  # Replace with your preferred MicroPython web framework

class RelayGPIOManager:
    """Manages GPIO pins for relay control, state, and safety."""
    def __init__(self, relay_pins, logger):
        self.relays = {name: Pin(pin, Pin.OUT) for name, pin in relay_pins.items()}
        self.logger = logger
        self.state = {name: False for name in relay_pins}

    def set_relay(self, name, state):
        if name in self.relays:
            self.relays[name].value(1 if state else 0)
            self.state[name] = bool(state)
            self.logger.log("INFO", "Relay set", relay=name, state=state)
            return True
        self.logger.log("WARN", "Invalid relay name", relay=name)
        return False

    def get_relay(self, name):
        return self.state.get(name, None)

    def all_states(self):
        return self.state.copy()

class RelaysController:
    """
    Production-grade RelaysController using the reusable IoT MicroPython library.
    Exposes REST API for secure relay control, supports all platform requirements.
    """

    def __init__(self, wifi_ssid, wifi_password, device_id, device_key, service_discovery_url, relay_pins, config_schema=None):
        self.device_id = device_id
        self.service_discovery_url = service_discovery_url
        self.network_manager = NetworkManager(wifi_ssid, wifi_password)
        self.auth_manager = AuthManager(device_key)
        self.config_manager = None
        self.watchdog_manager = None
        self.state_manager = None
        self.logger = Logger(mask_fields=["token", "password"])
        self.ntp_manager = None
        self.alarm_manager = None
        self.ota_manager = None

        self.state_server_url = None
        self.config_server_url = None
        self.alarm_server_url = None
        self.ota_server_url = None

        self.current_config = None
        self.network_ready_event = asyncio.Event()
        self.config_schema = config_schema

        self.relay_manager = RelayGPIOManager(relay_pins, self.logger)

        # REST API app (picoweb or similar)
        self.app = picoweb.WebApp(__name__) if picoweb else None

    async def wait_for_network(self):
        while not self.network_manager.connected:
            await asyncio.sleep(1)
        self.network_ready_event.set()

    async def register_with_service_discovery(self):
        await self.network_ready_event.wait()
        headers = self.auth_manager.get_auth_header()
        payload = {"device_id": self.device_id}
        while True:
            try:
                import urequests
                resp = urequests.post(self.service_discovery_url + "/register", headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    self.state_server_url = data.get("state_server_url")
                    self.config_server_url = data.get("config_server_url")
                    self.alarm_server_url = data.get("alarm_server_url")
                    self.ota_server_url = data.get("ota_server_url")
                    self.logger.log("INFO", "Registered with ServiceDiscovery", state_server=self.state_server_url, config_server=self.config_server_url)
                    self.config_manager = ConfigManager(self.config_server_url, self.auth_manager, self.device_id, schema=self.config_schema)
                    self.state_manager = StateManager(self.state_server_url, self.auth_manager, self.device_id)
                    self.watchdog_manager = WatchdogManager(self.service_discovery_url, self.auth_manager, self.device_id)
                    self.ntp_manager = TimeSyncManager(["pool.ntp.org", "time.google.com"])
                    self.alarm_manager = AlarmManager(self.alarm_server_url, self.auth_manager, self.device_id)
                    self.ota_manager = OTAUpdateManager(self.ota_server_url, self.auth_manager)
                    self.config_manager.set_update_callback(self.apply_config)
                    return
                else:
                    self.logger.log("ERROR", "Registration failed", status_code=resp.status_code, response=resp.text)
            except Exception as e:
                self.logger.log("ERROR", "Registration exception", error=str(e))
            await asyncio.sleep(5)

    async def apply_config(self, config):
        self.logger.log("INFO", "Applying new configuration", config=config)
        self.current_config = config
        # Example: Update relay logic, watchdog, etc. based on config
        if 'watchdog_interval' in config and self.watchdog_manager:
            self.watchdog_manager.interval = config['watchdog_interval']
        if 'config_fetch_interval' in config and self.config_manager:
            self.config_manager.fetch_interval = config['config_fetch_interval']
        if self.state_manager and self.watchdog_manager:
            await self.state_manager.update_state({
                "watchdog_interval": self.watchdog_manager.interval,
                "watchdog_timeout": self.watchdog_manager.interval * 3,
                "relays": self.relay_manager.all_states()
            })

    # --- REST API Handlers ---
    async def relay_set_handler(self, req, resp):
        data = await req.json()
        relay = req.url_match.group(1)
        state = data.get("state")
        token = req.headers.get("Authorization", "").replace("Bearer ", "")
        if not await self._authenticate(token, required_role="relay_control"):
            await resp.awrite("401 Unauthorized")
            return
        success = self.relay_manager.set_relay(relay, state == "HIGH")
        await resp.awrite("200 OK" if success else "400 Bad Request")

    async def relay_get_handler(self, req, resp):
        relay = req.url_match.group(1)
        state = self.relay_manager.get_relay(relay)
        await resp.awrite("200 OK\n" + str(state))

    async def relays_all_handler(self, req, resp):
        await resp.awrite("200 OK\n" + str(self.relay_manager.all_states()))

    async def _authenticate(self, token, required_role=None):
        if not token or self.auth_manager.is_token_expired():
            return False
        if required_role and not self.auth_manager.has_role(required_role):
            return False
        return True

    def setup_routes(self):
        if not self.app:
            return
        self.app.route("/gpio/<relay>", methods=["POST"])(self.relay_set_handler)
        self.app.route("/gpio/<relay>", methods=["GET"])(self.relay_get_handler)
        self.app.route("/gpio", methods=["GET"])(self.relays_all_handler)

    async def watchdog_loop(self):
        if self.watchdog_manager:
            await self.watchdog_manager.watchdog_loop()

    async def fetch_config_loop(self):
        if self.config_manager:
            await self.config_manager.fetch_config_loop()

    async def time_sync_loop(self):
        if self.ntp_manager:
            await self.ntp_manager.sync_loop()

    async def run_rest_api(self):
        if self.app:
            self.setup_routes()
            import socket
            # Listen on port 8080 by default
            self.app.run(host="0.0.0.0", port=8080, debug=True)

    async def main(self):
        await self.network_manager.connect()
        asyncio.create_task(self.network_manager.monitor())
        asyncio.create_task(self.wait_for_network())
        await self.network_ready_event.wait()
        await self.register_with_service_discovery()
        tasks = [
            asyncio.create_task(self.watchdog_loop()),
            asyncio.create_task(self.fetch_config_loop()),
            asyncio.create_task(self.time_sync_loop()),
            asyncio.create_task(self.run_rest_api())
        ]
        await asyncio.gather(*tasks)

# Usage example
async def run():
    relay_pins = {"relay1": 2, "relay2": 3}  # Example: GPIO2 and GPIO3
    controller = RelaysController(
        wifi_ssid="<your_wifi_ssid>",
        wifi_password="<your_wifi_password>",
        device_id="<unique_device_id>",
        device_key="<your_device_key>",
        service_discovery_url="https://<service_discovery_host>/api/devices",
        relay_pins=relay_pins
    )
    await controller.main()

# To run on your device, uncomment:
# asyncio.run(run())
