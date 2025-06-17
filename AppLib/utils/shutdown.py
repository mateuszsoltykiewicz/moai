"""
Graceful shutdown and signal handling utilities.

- Catch SIGTERM/SIGINT and trigger cleanup hooks.
- Async and sync support.
"""

import signal
import asyncio
import logging

def register_shutdown_handler(cleanup_callback, logger: logging.Logger):
    """
    Register a shutdown handler for SIGTERM/SIGINT.
    """
    def handler(signum, frame):
        logger.info("Received signal %s, running cleanup...", signum)
        cleanup_callback()
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

async def async_register_shutdown_handler(cleanup_coroutine, logger: logging.Logger):
    """
    Register an async shutdown handler for SIGTERM/SIGINT.
    """
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(cleanup_coroutine()))
    logger.info("Async shutdown handlers registered.")
