from contextlib import asynccontextmanager
from subservices.adapters.i2c import I2CAdapter

@asynccontextmanager
async def i2c_session(adapter_id: str):
    """Context manager for I2C adapter sessions"""
    adapter = I2CAdapter(adapter_id)
    try:
        await adapter.start()
        yield adapter
    finally:
        await adapter.stop()
