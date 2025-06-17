from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CertificateInfo(BaseModel):
    subject: str = Field(..., description="Certificate subject (e.g., CN=client,O=example,C=US)")
    issuer: str = Field(..., description="Certificate issuer")
    not_before: datetime = Field(..., description="Certificate validity start (ISO8601)")
    not_after: datetime = Field(..., description="Certificate validity end (ISO8601)")
    fingerprint: str = Field(..., description="Certificate fingerprint")
    serial_number: str = Field(..., description="Certificate serial number")

    class Config:
        schema_extra = {
            "example": {
                "subject": "CN=client,O=example,C=US",
                "issuer": "CN=Example CA,O=example,C=US",
                "not_before": "2025-06-01T00:00:00Z",
                "not_after": "2025-07-01T00:00:00Z",
                "fingerprint": "AB:CD:EF:12:34:56:78:90",
                "serial_number": "1234567890ABCDEF"
            }
        }

class MTLSStatusResponse(BaseModel):
    mtls: bool = Field(..., description="Whether mTLS was used")
    client_cert: Optional[CertificateInfo] = Field(None, description="Client certificate details (if mTLS used)")
    message: Optional[str] = Field(None, description="Status or error message")

    class Config:
        schema_extra = {
            "example": {
                "mtls": True,
                "client_cert": {
                    "subject": "CN=client,O=example,C=US",
                    "issuer": "CN=Example CA,O=example,C=US",
                    "not_before": "2025-06-01T00:00:00Z",
                    "not_after": "2025-07-01T00:00:00Z",
                    "fingerprint": "AB:CD:EF:12:34:56:78:90",
                    "serial_number": "1234567890ABCDEF"
                },
                "message": "mTLS handshake successful"
            }
        }
