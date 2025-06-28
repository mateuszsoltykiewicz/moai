from kubernetes import client
from .schemas import AdmissionReviewRequest, AdmissionReviewResponse, AdmissionResponse
from Library.registry.manager import ServiceRegistryManager  # To check service registration
from Library.config.manager import ConfigManager  # To get allowed services
from Library.logging import get_logger

logger = get_logger(__name__)

class AdmissionManager:
    def __init__(self):
        self.registry = ServiceRegistryManager()
        self.config = ConfigManager()

    async def validate_pod(self, request: AdmissionReviewRequest) -> AdmissionReviewResponse:
        pod = request.request["object"]
        service_name = pod["metadata"]["labels"].get("app")
        
        # 1. Check if service is allowed via config
        allowed_services = await self.config.get("allowed_services")  # e.g., ["alarms", "state"]
        if service_name not in allowed_services:
            logger.info(f"Pod denied: {service_name} not in allowlist")
            return self._deny(f"Service {service_name} not in allowlist")
        
        # 2. Check if service is registered in ServiceRegistry
        if not await self.registry.is_service_registered(service_name):
            logger.info(f"Pod denied: {service_name} not registered")
            return self._deny(f"Service {service_name} not registered")
        
        # 3. Check pod security policies (e.g., no privileged containers)
        if self._is_privileged(pod):
            logger.info(f"Pod denied: privileged containers not allowed for {service_name}")
            return self._deny("Privileged pods not allowed")
        
        logger.info(f"Pod allowed: {service_name}")
        return self._allow()

    def _allow(self) -> AdmissionReviewResponse:
        return AdmissionReviewResponse(
            response=AdmissionResponse(uid="", allowed=True)
        )

    def _deny(self, message: str) -> AdmissionReviewResponse:
        return AdmissionReviewResponse(
            response=AdmissionResponse(uid="", allowed=False, status={"message": message})
        )

    def _is_privileged(self, pod: dict) -> bool:
        for container in pod["spec"]["containers"]:
            security_context = container.get("securityContext", {})
            if security_context.get("privileged", False):
                return True
        return False
