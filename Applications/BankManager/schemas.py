from pydantic import BaseModel, Field
from typing import Optional

class TransactionRequest(BaseModel):
    id: str = Field(..., example="txn-001")
    account_id: str = Field(..., example="acc-123")
    amount: float = Field(..., example=100.0)
    currency: str = Field(..., example="USD")

class TransactionResponse(BaseModel):
    id: str
    status: str
    amount: float
