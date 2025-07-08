import asyncio
import time
from typing import Dict, List, Any, Optional
from .schemas import ServiceInstance, RegisterRequest, HeartbeatRequest, DeregisterRequest
from .exceptions import ServiceNotFoundError, InstanceNotFoundError
from .metrics import record_registry_operation, update_registered_instances
from Library.logging import get_logger

logger = get_logger(__name__)

class ServiceRegistryManager:
    def __init__(self, heartbeat_timeout: int = 30):
        self._services: Dict[str, Dict[str, ServiceInstance]] = {}
        self._lock = asyncio.Lock()
        self.heartbeat_timeout = heartbeat_timeout

    async def register(self, req: RegisterRequest):
        async with self._lock:
            now = time.time()
            instance = ServiceInstance(
                service_name=req.service_name,
                instance_id=req.instance_id,
                host=req.host,
                port=req.port,
                version=req.version,
                metadata=req.metadata or {},
                last_heartbeat=now,
                healthy=True
            )
            if req.service_name not in self._services:
                self._services[req.service_name] = {}
            self._services[req.service_name][req.instance_id] = instance
            update_registered_instances(req.service_name, len(self._services[req.service_name]))
            record_registry_operation("register")
            logger.info(f"Registered {req.service_name}:{req.instance_id} at {req.host}:{req.port}")

    async def heartbeat(self, req: HeartbeatRequest):
        async with self._lock:
            svc = self._services.get(req.service_name)
            if not svc or req.instance_id not in svc:
                raise InstanceNotFoundError(f"Instance {req.instance_id} not found for {req.service_name}")
            svc[req.instance_id].last_heartbeat = time.time()
            svc[req.instance_id].healthy = True
            record_registry_operation("heartbeat")
            logger.debug(f"Heartbeat received for {req.service_name}:{req.instance_id}")

    async def deregister(self, req: DeregisterRequest):
        async with self._lock:
            svc = self._services.get(req.service_name)
            if not svc or req.instance_id not in svc:
                raise InstanceNotFoundError(f"Instance {req.instance_id} not found for {req.service_name}")
            del svc[req.instance_id]
            update_registered_instances(req.service_name, len(svc))
            record_registry_operation("deregister")
            logger.info(f"Deregistered {req.service_name}:{req.instance_id}")

    async def list_services(self) -> Dict[str, List[ServiceInstance]]:
        async with self._lock:
            result = {}
            now = time.time()
            for svc_name, instances in self._services.items():
                # Filter out unhealthy/expired
                healthy_instances = [
                    inst for inst in instances.values()
                    if now - inst.last_heartbeat < self.heartbeat_timeout and inst.healthy
                ]
                result[svc_name] = healthy_instances
                update_registered_instances(svc_name, len(healthy_instances))
            record_registry_operation("list_services")
            return result

    async def get_service_instance(self, service_name: str, instance_id: str) -> ServiceInstance:
        async with self._lock:
            svc = self._services.get(service_name)
            if not svc or instance_id not in svc:
                raise InstanceNotFoundError(f"Instance {instance_id} not found for {service_name}")
            return svc[instance_id]

    async def cleanup(self):
        """Remove expired/unhealthy instances (run periodically)."""
        async with self._lock:
            now = time.time()
            for svc_name, instances in list(self._services.items()):
                for inst_id, inst in list(instances.items()):
                    if now - inst.last_heartbeat > self.heartbeat_timeout:
                        del instances[inst_id]
                        logger.info(f"Cleaned up expired instance {svc_name}:{inst_id}")
                update_registered_instances(svc_name, len(instances))
