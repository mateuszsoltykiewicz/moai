from pydantic import BaseModel, Field
from typing import Optional

class MTLSStatusResponse(BaseModel):
    mtls: bool = Field(..., description="Whether mTLS was used")
    client_cert: Optional[str] = Field(None, description="Client certificate info")
    message: Optional[str] = Field(None, description="Status message")