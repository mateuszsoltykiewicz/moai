"""
Pydantic schemas for MtlsManager.
"""

from pydantic import BaseModel, Field

class MtlsConfig(BaseModel):
    enforce: bool = Field(default=False, description="Enforce mTLS for all APIs")
    server_cert: str = Field(..., description="Path to server certificate (injected by cert-manager)")
    server_key: str = Field(..., description="Path to server private key (injected by cert-manager)")
    ca_cert: str = Field(..., description="Path to CA certificate (injected by cert-manager)")
