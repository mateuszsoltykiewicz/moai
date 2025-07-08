# /Python/libraries/core/async_exception_handling/__init__.py
import logging

async def handle_exception(e, logger=None, context=None):
    msg = f"Exception: {str(e)}"
    if context:
        msg += f" | Context: {context}"
    if logger:
        logger.error(msg)
    else:
        print(msg)
