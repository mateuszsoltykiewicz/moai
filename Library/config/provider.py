import abc
from typing import Any, AsyncGenerator

class ConfigProvider(abc.ABC):
    @abc.abstractmethod
    async def setup(self):
        pass

    @abc.abstractmethod
    async def teardown(self):
        pass

    @abc.abstractmethod
    async def load(self) -> dict:
        pass

    @abc.abstractmethod
    async def watch(self) -> AsyncGenerator[None, None]:
        yield
