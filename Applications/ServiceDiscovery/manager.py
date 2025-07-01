import asyncio
from typing import List, Dict
from Library.vault import VaultManager
from Library.alarms import AlarmClient
from Library.registry import RegistryClient
from Library.logging import get_logger
from kubernetes import client, config as k8s_config

logger = get_logger(__name__)

class ServiceDiscoveryManager:
    _allowed_services = set()
    _discovered_services = {}
    _lock = asyncio.Lock()

    @classmethod
    async def setup(cls):
        try:
            k8s_config.load_incluster_config()
            logger.info("Kubernetes in-cluster config loaded")
        except Exception:
            k8s_config.load_kube_config()
            logger.info("Kubernetes local config loaded")

        await cls._load_allowed_services()
        asyncio.create_task(cls._discovery_loop())
        await RegistryClient.register_service(name="service-discovery", url="http://service-discovery:8000")

    @classmethod
    async def shutdown(cls):
        logger.info("ServiceDiscoveryManager shutdown complete")

    @classmethod
    async def _load_allowed_services(cls):
        secret = await VaultManager.read_secret("secret/allowed_services")
        services = secret.get("services", [])
        cls._allowed_services = set(services)
        logger.info(f"Allowed services loaded: {cls._allowed_services}")

    @classmethod
    async def _discovery_loop(cls):
        v1 = client.CoreV1Api()
        while True:
            try:
                await cls._load_allowed_services()
                ret = v1.list_service_for_all_namespaces(watch=False)
                discovered = set()
                for svc in ret.items:
                    svc_name = svc.metadata.name
                    discovered.add(svc_name)
                    if svc_name not in cls._allowed_services:
                        logger.warning(f"Unauthorized service detected: {svc_name}")
                        await AlarmClient.raise_alarm(
                            alarm_id="UNAUTHORIZED_SERVICE",
                            message=f"Unauthorized service detected: {svc_name}",
                            severity="FATAL"
                        )
                        logger.error(f"Attempting to terminate unauthorized service: {svc_name}")
                        # TODO: Implement actual termination logic via K8s API

                async with cls._lock:
                    cls._discovered_services = {svc: "healthy" for svc in discovered if svc in cls._allowed_services}

                for svc in cls._discovered_services:
                    await RegistryClient.update_service_status(svc, "healthy")

            except Exception as e:
                logger.error(f"Error during service discovery: {e}")

            await asyncio.sleep(10)

    @classmethod
    async def list_services(cls) -> Dict[str, str]:
        async with cls._lock:
            return cls._discovered_services.copy()

    @classmethod
    async def get_allowed_services(cls) -> List[str]:
        return list(cls._allowed_services)
