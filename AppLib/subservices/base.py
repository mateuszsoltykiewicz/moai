from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from AppLib.subservices.config.service import ConfigService
from AppLib.subservices.event_engine import EventEngine

class BaseSubService(ABC):
    def __init__(
        self,
        config_service: ConfigService,
        event_engine: EventEngine,
        config_section: str,
        schema_path: str
    ):
        self.config_service = config_service
        self.event_engine = event_engine
        self.config_section = config_section
        self.schema_path = schema_path
        self._current_config: Optional[Dict] = None

    async def start(self):
        """Start the subservice with config validation and event registration."""
        config = self.config_service.get().get(self.config_section)
        if not config:
            raise ValueError(f"Missing config section: {self.config_section}")
        
        # Validate against schema
        validate_config(config, load_schema(self.schema_path), self.config_section)
        
        # Initialize service
        await self._start_service(config)
        
        # Register for config changes
        self.config_service.register_listener(self._on_config_change)
        
        # Register event handlers
        await self._register_event_handlers()

    async def _on_config_change(self, new_config: Dict):
        """Handle config updates with validation and hot-reload."""
        new_subconfig = new_config.get(self.config_section)
        if new_subconfig:
            try:
                validate_config(new_subconfig, load_schema(self.schema_path), self.config_section)
                await self._reload_service(new_subconfig)
                self._current_config = new_subconfig
                await self.event_engine.produce(
                    topic="config_updated",
                    value={"service": self.config_section, "status": "reloaded"}
                )
            except ConfigValidationError as e:
                await self.event_engine.produce(
                    topic="config_error",
                    value={"service": self.config_section, "error": str(e)}
                )

    @abstractmethod
    async def _start_service(self, config: Dict):
        """Subservice-specific initialization."""

    @abstractmethod
    async def _reload_service(self, new_config: Dict):
        """Subservice-specific reload logic."""

    @abstractmethod
    async def _register_event_handlers(self):
        """Register event listeners with EventEngine."""

    @abstractmethod
    async def stop(self):
        """Cleanup resources."""
