from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class ServiceInstance(BaseModel):
    service_name: str
    instance_id: str
    host: str
    port: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: Optional[str] = None
    last_heartbeat: float
    healthy: bool = True

class RegisterRequest(BaseModel):
    service_name: str
    instance_id: str
    host: str
    port: int
    version: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class HeartbeatRequest(BaseModel):
    service_name: str
    instance_id: str

class DeregisterRequest(BaseModel):
    service_name: str
    instance_id: str

class ServiceListResponse(BaseModel):
    services: Dict[str, List[ServiceInstance]]

class ServiceInstanceResponse(BaseModel):
    instance: ServiceInstance
