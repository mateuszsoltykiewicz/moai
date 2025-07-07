# /Python/libraries/core/async_retry_helpers/__init__.py
import asyncio
import functools

def async_retry(max_attempts=3, delay=1, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
