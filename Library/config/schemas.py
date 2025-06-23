"""
Pydantic schemas for ConfigManager.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class AppConfig(BaseModel):
    # Example fields, extend as needed
    app_name: str = Field(..., example="MyApp")
    version: str = Field(..., example="1.0.0")
    components: Dict[str, bool] = Field(default_factory=dict)
    # Add more config fields as needed
