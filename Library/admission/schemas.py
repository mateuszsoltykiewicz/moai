from pydantic import BaseModel
from typing import Optional, Any, Dict

class AdmissionResponse(BaseModel):
    uid: str = ""
    allowed: bool
    status: Optional[Dict[str, Any]] = None

class AdmissionReviewRequest(BaseModel):
    apiVersion: str
    kind: str
    request: Dict[str, Any]  # Full Kubernetes AdmissionRequest

class AdmissionReviewResponse(BaseModel):
    apiVersion: str = "admission.k8s.io/v1"
    kind: str = "AdmissionReview"
    response: AdmissionResponse
