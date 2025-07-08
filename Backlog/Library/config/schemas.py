from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class AppConfig(BaseModel):
    app_name: str = Field(..., example="MyApp")
    version: str = Field(..., example="1.0.0")
    components: Dict[str, bool] = Field(default_factory=dict)
    # Extend as needed
