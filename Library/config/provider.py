# config/provider.py
import abc
from typing import Any, AsyncGenerator

class ConfigProvider(abc.ABC):
    @abc.abstractmethod
    async def setup(self):
        """Initialize provider connections"""
        pass

    @abc.abstractmethod
    async def teardown(self):
        """Cleanup provider resources"""
        pass

    @abc.abstractmethod
    async def load(self) -> dict:
        """Load configuration data"""
        pass

    @abc.abstractmethod
    async def watch(self) -> AsyncGenerator[None, None]:
        """Watch for configuration changes"""
        yield
