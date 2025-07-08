import asyncio
from hap_server import HAPServer
from ws_client import WebSocketAccessoryClient
from Library.logging import setup_logging

logger = setup_logging(__name__)

async def main():
    hap_server = HAPServer()
    ws_client = WebSocketAccessoryClient(hap_server)
    await ws_client.connect_and_listen()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("HomeKitProtocolBridge stopped by user")
