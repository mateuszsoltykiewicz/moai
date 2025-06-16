from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CertificateInfo(BaseModel):
    subject: str
    issuer: str
    not_before: datetime
    not_after: datetime
    fingerprint: str
    serial_number: str
    valid: bool = True

class MTLSStatus(BaseModel):
    mtls_enabled: bool
    certificate: Optional[CertificateInfo]
    error: Optional[str] = None
