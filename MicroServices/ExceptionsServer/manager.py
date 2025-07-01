from datetime import datetime
from typing import List, Optional
from .models import ExceptionRecord
from .schemas import ExceptionCreate, ExceptionRead
from Library.database import DatabaseManager
from Library.vault import VaultManager
from Library.alarms import AlarmClient
from Library.logging import get_logger

logger = get_logger(__name__)

class ExceptionsManager:
    _db = DatabaseManager(db_name="exceptions_db")
    _vault = VaultManager()
    _alarms = AlarmClient()

    @classmethod
    async def setup(cls):
        await cls._db.ensure_database()
        await cls._db.create_tables([ExceptionRecord])
        logger.info("ExceptionsManager setup complete")

    @classmethod
    async def shutdown(cls):
        await cls._db.shutdown()
        logger.info("ExceptionsManager shutdown complete")

    @classmethod
    async def get_allowed_services(cls) -> List[str]:
        secret = await cls._vault.read_secret("secret/allowed_services")
        return secret.get("services", [])

    @classmethod
    async def create_exception(cls, exc: ExceptionCreate) -> ExceptionRead:
        allowed = await cls.get_allowed_services()
        if exc.service not in allowed:
            await cls._alarms.raise_alarm(
                alarm_id="UNAUTHORIZED_SERVICE",
                message=f"Unauthorized service detected: {exc.service}",
                severity="FATAL"
            )
            await cls._alarms.fail_service(exc.service)
            raise PermissionError(f"Service {exc.service} is not authorized. Security alarm raised.")
        record = ExceptionRecord(
            exception_name=exc.exception_name,
            service=exc.service,
            status=exc.status,
            last_change=exc.last_change or datetime.utcnow()
        )
        await cls._db.add(record)
        return ExceptionRead.from_orm(record)

    @classmethod
    async def list_exceptions(cls, service: Optional[str] = None, status: Optional[str] = None) -> List[ExceptionRead]:
        filters = {}
        if service:
            filters["service"] = service
        if status:
            filters["status"] = status
        records = await cls._db.query(ExceptionRecord, **filters)
        return [ExceptionRead.from_orm(r) for r in records]
