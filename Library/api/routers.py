# api/routers.py

from Library.core.api import router as core_router
from Library.config.api import router as config_router
from Library.state.api import router as state_router
from Library.secrets.api import router as secrets_router
from Library.metrics.api import router as metrics_router
from Library.tracing.api import router as tracing_router
from Library.health.api import router as health_router
from Library.utils.api import router as utils_router
from Library.alarms.api import router as alarms_router
from Library.sessions.api import router as sessions_router
from Library.schemas.api import router as schemas_router

# Optional routers (import only if enabled)
def get_all_routers(config):
    routers = [
        core_router,
        config_router,
        state_router,
        secrets_router,
        metrics_router,
        tracing_router,
        health_router,
        utils_router,
        alarms_router,
        sessions_router,
        schemas_router,
    ]

    # Dynamically add optional routers based on config
    if config.enabled_components.get("kafka"):
        from Library.kafka.api import router as kafka_router
        routers.append(kafka_router)
    if config.enabled_components.get("i2c"):
        from Library.i2c.api import router as i2c_router
        routers.append(i2c_router)
    if config.enabled_components.get("canbus"):
        from Library.canbus.api import router as canbus_router
        routers.append(canbus_router)
    if config.enabled_components.get("database"):
        from Library.database.api import router as database_router
        routers.append(database_router)
    if config.enabled_components.get("mtls"):
        from Library.mtls.api import router as mtls_router
        routers.append(mtls_router)
    if config.enabled_components.get("hap"):
        from Library.hap.api import router as hap_router
        routers.append(hap_router)
    # ...add more as needed

    return routers
