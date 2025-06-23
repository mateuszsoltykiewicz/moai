"""
Secrets management and redaction utilities.

- Secure loading of secrets from env, files, or secret managers.
- Redact sensitive fields in logs and errors.
"""

import os
from typing import Optional, List, Dict

def load_secret(name: str, default: Optional[str] = None) -> str:
    """
    Load a secret from environment variables or fallback to default.
    """
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required secret: {name}")
    return value

def redact_sensitive(data: Dict, fields: List[str]) -> Dict:
    """
    Redact sensitive fields in a dictionary.
    """
    redacted = data.copy()
    for field in fields:
        if field in redacted:
            redacted[field] = "***REDACTED***"
    return redacted
