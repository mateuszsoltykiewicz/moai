"""
Enhanced schemas with certificate metadata.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any
from datetime import datetime

class CertificateInfo(BaseModel):
    subject: str
    issuer: str
    not_valid_before: str
    not_valid_after: str
    serial_number: str
    signature_algorithm: str

class MtlsConfig(BaseModel):
    enforce: bool = Field(..., description="Enforce mTLS for all APIs")
    server_cert: str = Field(..., description="Path to server certificate")
    server_key: str = Field(..., description="Path to server private key")
    ca_cert: str = Field(..., description="Path to CA certificate")
    cert_info: Dict[str, CertificateInfo] = Field(..., description="Parsed certificate metadata")

    @validator('server_cert', 'server_key', 'ca_cert')
    def path_must_exist(cls, v):
        if not Path(v).exists():
            raise ValueError(f"File does not exist: {v}")
        return v
