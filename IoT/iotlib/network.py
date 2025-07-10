from uasyncio import asyncio
import network

# --- Network Controller ---
class NetworkController:
    """
    Handles WiFi connectivity and monitors for network loss.
    """
    def __init__(self, network_name, network_pass):
        self._network_name = network_name
        self._network_pass = network_pass
        self._wlan = network.WLAN(network.STA_IF)

    async def connect(self):
        """
        Connect to WiFi network.
        """
        self._wlan.active(True)
        self._wlan.connect(self._network_name, self._network_pass)
        return self._wlan

    async def network_monitor(self, config):
        """
        Async task: Monitor WiFi connection, trigger disaster if lost.
        """
        while self._wlan.isconnected():
            await asyncio.sleep(1)
        config.disaster_detected = True
        config.exit_code = 10
        config.disaster_reason.append("Network Lost!")
