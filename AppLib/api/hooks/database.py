from core.logging import get_logger
from schemas.database import DatabaseRecordCreate

async def validate_create(request: DatabaseRecordCreate, user: dict):
    """Validate record creation"""
    if "restricted" in request.data and "admin" not in user.roles:
        return {"valid": False, "message": "Admin role required for restricted data"}
    return {"valid": True}

async def audit_create(record: dict, user: dict):
    """Audit record creation"""
    logger.info(f"User {user.sub} created record {record['id']}")
