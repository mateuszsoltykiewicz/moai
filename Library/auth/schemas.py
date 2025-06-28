from pydantic import BaseModel
from typing import List, Dict, Any

class AuthContext(BaseModel):
    subject: str
    roles: List[str]
    claims: Dict[str, Any]
