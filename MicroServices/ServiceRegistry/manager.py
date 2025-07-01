import asyncio
import time
from typing import Dict, List, Any
from .schemas import ServiceInstance, RegisterRequest, HeartbeatRequest, DeregisterRequest
from .metrics import record_registry_operation, update_registered_instances
from Library.logging import get_logger

logger = get_logger(__name__)

class ServiceRegistryManager:
    _services: Dict[str, Dict[str, ServiceInstance]] = {}
    _lock = asyncio.Lock()
    heartbeat_timeout = 30

    @classmethod
    async def setup(cls):
        logger.info("ServiceRegistryManager setup complete.")

    @classmethod
    async def shutdown(cls):
        logger.info("ServiceRegistryManager shutdown complete.")

    @classmethod
    async def register(cls, req: RegisterRequest):
        async with cls._lock:
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
            if req.service_name not in cls._services:
                cls._services[req.service_name] = {}
            cls._services[req.service_name][req.instance_id] = instance
            update_registered_instances(req.service_name, len(cls._services[req.service_name]))
            record_registry_operation("register")
            logger.info(f"Registered {req.service_name}:{req.instance_id} at {req.host}:{req.port}")

    @classmethod
    async def heartbeat(cls, req: HeartbeatRequest):
        async with cls._lock:
            svc = cls._services.get(req.service_name)
            if not svc or req.instance_id not in svc:
                raise Exception(f"Instance {req.instance_id} not found for {req.service_name}")
            svc[req.instance_id].last_heartbeat = time.time()
            svc[req.instance_id].healthy = True
            record_registry_operation("heartbeat")
            logger.debug(f"Heartbeat for {req.service_name}:{req.instance_id}")

    @classmethod
    async def deregister(cls, req: DeregisterRequest):
        async with cls._lock:
            svc = cls._services.get(req.service_name)
            if not svc or req.instance_id not in svc:
                raise Exception(f"Instance {req.instance_id} not found for {req.service_name}")
            del svc[req.instance_id]
            update_registered_instances(req.service_name, len(svc))
            record_registry_operation("deregister")
            logger.info(f"Deregistered {req.service_name}:{req.instance_id}")

    @classmethod
    async def list_services(cls) -> Dict[str, List[ServiceInstance]]:
        async with cls._lock:
            result = {}
            now = time.time()
            for svc_name, instances in cls._services.items():
                healthy_instances = [
                    inst for inst in instances.values()
                    if now - inst.last_heartbeat < cls.heartbeat_timeout and inst.healthy
                ]
                result[svc_name] = healthy_instances
                update_registered_instances(svc_name, len(healthy_instances))
            record_registry_operation("list_services")
            return result

    @classmethod
    async def get_service_instance(cls, service_name: str, instance_id: str) -> ServiceInstance:
        async with cls._lock:
            svc = cls._services.get(service_name)
            if not svc or instance_id not in svc:
                raise Exception(f"Instance {instance_id} not found for {service_name}")
            return svc[instance_id]
