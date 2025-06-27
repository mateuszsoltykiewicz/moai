# events/registry.py

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Literal

# ---- Alarm Events ----
class AlarmRaisedEvent(BaseModel):
    event_type: Literal["AlarmRaised"] = "AlarmRaised"
    id: str
    source: str
    type: str
    details: Dict[str, Any]
    timestamp: str

class AlarmClearedEvent(BaseModel):
    event_type: Literal["AlarmCleared"] = "AlarmCleared"
    id: str
    cleared_by: str
    timestamp: str

# ---- State Events ----
class ServiceRegisteredEvent(BaseModel):
    event_type: Literal["ServiceRegistered"] = "ServiceRegistered"
    name: str
    version: str
    endpoints: Dict[str, str]
    meta: Optional[Dict[str, Any]] = None
    timestamp: str

class ServiceUnhealthyEvent(BaseModel):
    event_type: Literal["ServiceUnhealthy"] = "ServiceUnhealthy"
    name: str
    reason: str
    timestamp: str

class ServiceHeartbeatEvent(BaseModel):
    event_type: Literal["ServiceHeartbeat"] = "ServiceHeartbeat"
    name: str
    status: str
    timestamp: str

# ---- Sensor Events ----
class SensorDataReceivedEvent(BaseModel):
    event_type: Literal["SensorDataReceived"] = "SensorDataReceived"
    sensor_id: str
    value: Any
    unit: Optional[str]
    quality: Optional[str]
    timestamp: str

class SensorAnomalyDetectedEvent(BaseModel):
    event_type: Literal["SensorAnomalyDetected"] = "SensorAnomalyDetected"
    sensor_id: str
    anomaly_type: str
    value: Any
    timestamp: str

# ---- Config/Secrets Events ----
class ConfigUpdatedEvent(BaseModel):
    event_type: Literal["ConfigUpdated"] = "ConfigUpdated"
    service: str
    version: str
    diff: Optional[Dict[str, Any]]
    updated_by: Optional[str]
    timestamp: str

class SecretsRotatedEvent(BaseModel):
    event_type: Literal["SecretsRotated"] = "SecretsRotated"
    service: str
    secrets: List[str]
    rotated_by: Optional[str]
    timestamp: str

# ---- Job/Command Events ----
class HeatingJobStartedEvent(BaseModel):
    event_type: Literal["HeatingJobStarted"] = "HeatingJobStarted"
    job_id: str
    params: Dict[str, Any]
    started_by: str
    timestamp: str

class HeatingJobStoppedEvent(BaseModel):
    event_type: Literal["HeatingJobStopped"] = "HeatingJobStopped"
    job_id: str
    status: str
    stopped_by: str
    timestamp: str

class DisasterDetectedEvent(BaseModel):
    event_type: Literal["DisasterDetected"] = "DisasterDetected"
    type: str
    source: str
    details: Dict[str, Any]
    timestamp: str

# ---- Audit/Telemetry Events ----
class UserActionEvent(BaseModel):
    event_type: Literal["UserActionEvent"] = "UserActionEvent"
    user: str
    action: str
    target: str
    metadata: Optional[Dict[str, Any]]
    timestamp: str

class TelemetryEvent(BaseModel):
    event_type: Literal["TelemetryEvent"] = "TelemetryEvent"
    service: str
    metrics: Dict[str, Any]
    timestamp: str

# ---- Accessory/Integration Events ----
class AccessoryAddedEvent(BaseModel):
    event_type: Literal["AccessoryAdded"] = "AccessoryAdded"
    accessory_id: str
    type: str
    state: Dict[str, Any]
    timestamp: str

class AccessoryRemovedEvent(BaseModel):
    event_type: Literal["AccessoryRemoved"] = "AccessoryRemoved"
    accessory_id: str
    timestamp: str

class AccessoryStateChangedEvent(BaseModel):
    event_type: Literal["AccessoryStateChanged"] = "AccessoryStateChanged"
    accessory_id: str
    new_state: Dict[str, Any]
    timestamp: str

# ---- Central Event Registry ----
event_registry = {
    "AlarmRaised": AlarmRaisedEvent,
    "AlarmCleared": AlarmClearedEvent,
    "ServiceRegistered": ServiceRegisteredEvent,
    "ServiceUnhealthy": ServiceUnhealthyEvent,
    "ServiceHeartbeat": ServiceHeartbeatEvent,
    "SensorDataReceived": SensorDataReceivedEvent,
    "SensorAnomalyDetected": SensorAnomalyDetectedEvent,
    "ConfigUpdated": ConfigUpdatedEvent,
    "SecretsRotated": SecretsRotatedEvent,
    "HeatingJobStarted": HeatingJobStartedEvent,
    "HeatingJobStopped": HeatingJobStoppedEvent,
    "DisasterDetected": DisasterDetectedEvent,
    "UserActionEvent": UserActionEvent,
    "TelemetryEvent": TelemetryEvent,
    "AccessoryAdded": AccessoryAddedEvent,
    "AccessoryRemoved": AccessoryRemovedEvent,
    "AccessoryStateChanged": AccessoryStateChangedEvent,
}
