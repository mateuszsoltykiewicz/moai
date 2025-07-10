from phew import server
import uasyncio as asyncio

from IoT.iotlib.network import NetworkController
from IoT.relays_controller.configuration import RelaysConfiguration
from IoT.iotlib.watchdog import WatchdogController
from IoT.iotlib.disaster import DisasterController
from IoT.sensors_controller.sensors_controller import SensorsController
from IoT.iotlib.shutdown import ShutdownController


# --- Main Application Entry Point ---
async def main(app):
    # Setup network and configuration
    network_controller = NetworkController()
    wlan = await asyncio.create_task(network_controller.connect())
    configuration = RelaysConfiguration(app=app, wlan=wlan)

    # Controllers
    watchdog_controller = WatchdogController(app=app, configuration=configuration)
    disaster_controller = DisasterController(configuration=configuration)
    sensors_controller = SensorsController(app=app, configuration=configuration)

    # Start monitoring tasks
    asyncio.create_task(disaster_controller.disaster_monitor())
    asyncio.create_task(configuration.validate_apis())

    tasks = [
        asyncio.create_task(watchdog_controller.watchdog_timeout()),
        asyncio.create_task(network_controller.network_monitor(config=configuration)),
    ]

    # Setup shutdown controller
    shutdown_controller = ShutdownController(
        app=app,
        config=configuration,
        tasks=tasks,
        shutdown_task=sensors_controller.shutdown_task
    )
    asyncio.create_task(shutdown_controller.should_shutdown())

# --- Application Startup ---
app = server.Phew()
asyncio.run(main(app=app))
