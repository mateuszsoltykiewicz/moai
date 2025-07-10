from phew import server
import uasyncio as asyncio

from IoT.iotlib.network import NetworkController
from IoT.relays_controller.configuration import RelaysConfiguration
from IoT.iotlib.watchdog import WatchdogController
from IoT.iotlib.disaster import DisasterController
from IoT.relays_controller.heating_controller import HeatingController
from IoT.iotlib.shutdown import ShutdownController


# --- Main Application Entry Point ---
async def main(app):
    # Setup network and configuration
    network_controller = NetworkController()
    wlan = await asyncio.create_task(network_controller.connect())
    remote_metrics_url = "http://<REMOTE_PICO_IP>/metrics"
    configuration = RelaysConfiguration(app=app, wlan=wlan, metrics_poll_url=remote_metrics_url)

    # Controllers
    watchdog_controller = WatchdogController(app=app, configuration=configuration)
    disaster_controller = DisasterController(configuration=configuration)
    heating_controller = HeatingController(app=app, configuration=configuration)

    # Start monitoring tasks
    asyncio.create_task(disaster_controller.disaster_monitor())
    asyncio.create_task(configuration.validate_apis())

    tasks = [
        asyncio.create_task(watchdog_controller.watchdog_timeout()),
        asyncio.create_task(network_controller.network_monitor(config=configuration)),
        asyncio.create_task(heating_controller.initialized()),
        asyncio.create_task(heating_controller.heating_on()),
        asyncio.create_task(heating_controller.heating_off()),
        asyncio.create_task(heating_controller.heating_monitor()),
        asyncio.create_task(heating_controller.fetch_remote_metrics()),
        asyncio.create_task(heating_controller.metrics_update_watchdog()),
        asyncio.create_task(heating_controller.metrics_analyzer())
    ]

    # Setup shutdown controller
    shutdown_controller = ShutdownController(
        app=app,
        config=configuration,
        tasks=tasks,
        shutdown_task=heating_controller.shutdown_task
    )
    asyncio.create_task(shutdown_controller.should_shutdown())

# --- Application Startup ---
app = server.Phew()
asyncio.run(main(app=app))
