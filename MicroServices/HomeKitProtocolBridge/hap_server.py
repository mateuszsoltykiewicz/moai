import asyncio
import json
import logging
import threading
import uuid
from pyhap.accessory_driver import AccessoryDriver
import websockets
from Library.vault import VaultManager
from Library.logging import setup_logging
from accessories.alarms import AlarmsAccessory
from accessories.heating import HeatingAccessory
from accessories.bank import BankAccessory

logger = setup_logging(__name__)

class HomeKitProtocolBridge:
    def __init__(self, ws_url="ws://homekitbridge:8000/ws/accessories", hap_port=51826):
        self.ws_url = ws_url
        self.hap_port = hap_port
        self.driver = None
        self.accessories = {}
        self.lock = threading.Lock()
        self.pairing_code = None
        self.setup_id = str(uuid.uuid4())[:4]  # Unique setup ID for QR code

    async def fetch_pairing_code(self):
        """Fetch pairing code from Vault with error handling and fallback"""
        try:
            secret = await VaultManager.read_secret("secret/homekit/pairing")
            return secret.get("code", "111-11-111")  # Fallback code
        except Exception as e:
            logger.error(f"Vault connection failed: {e}")
            return "222-22-222"  # Secondary fallback

    async def start_hap_server(self):
        """Start HAP server with pairing code from Vault"""
        self.pairing_code = await self.fetch_pairing_code()
        
        # Configure and start driver
        self.driver = AccessoryDriver(
            port=self.hap_port,
            pincode=self.pairing_code,
            persist_file="./homekit.state"
        )
        
        logger.info(f"HAP server starting on port {self.hap_port}")
        logger.info(f"HomeKit Pairing Code: {self.pairing_code}")
        logger.info(f"HomeKit Setup ID: {self.setup_id}")
        
        # Start in background thread
        driver_thread = threading.Thread(target=self.driver.start)
        driver_thread.daemon = True
        driver_thread.start()

    def create_accessory(self, acc_type, data):
        """Factory method for creating accessories"""
        try:
            if acc_type == "alarm":
                return AlarmsAccessory(aid=int(data['id']), **data)
            elif acc_type == "heating":
                return HeatingAccessory(aid=int(data['id']), **data)
            elif acc_type == "bank":
                return BankAccessory(aid=int(data['id']), **data)
        except KeyError as e:
            logger.error(f"Missing required field: {e}")
        except Exception as e:
            logger.error(f"Accessory creation failed: {e}")
        return None

    async def handle_accessory_update(self, data):
        """Create/update accessory with thread-safe locking"""
        with self.lock:
            acc_id = data['id']
            if acc_id not in self.accessories:
                accessory = self.create_accessory(data['type'], data)
                if accessory:
                    self.driver.add_accessory(accessory)
                    self.accessories[acc_id] = accessory
                    logger.info(f"Added accessory {acc_id}")
            else:
                self.accessories[acc_id].update_from_dict(data)
                logger.debug(f"Updated accessory {acc_id}")

    async def websocket_listener(self):
        """Main WebSocket listener with reconnection logic"""
        while True:
            try:
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=30,
                    max_queue=100
                ) as websocket:
                    logger.info(f"Connected to HomeKitBridge at {self.ws_url}")
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            await self.handle_accessory_update(data)
                        except json.JSONDecodeError:
                            logger.error("Invalid JSON received")
                        except Exception as e:
                            logger.error(f"Message handling error: {e}")
            except (websockets.ConnectionClosed, ConnectionError) as e:
                logger.warning(f"Connection lost: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"WebSocket error: {e}. Retrying in 10s...")
                await asyncio.sleep(10)

    async def run(self):
        """Main entry point"""
        await self.start_hap_server()
        await self.websocket_listener()

async def main():
    bridge = HomeKitProtocolBridge()
    await bridge.run()

if __name__ == "__main__":
    asyncio.run(main())
