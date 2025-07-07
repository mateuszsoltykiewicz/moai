# /Python/libraries/core/uuid_correlation/__init__.py
import uuid
import contextvars

service_uuid = str(uuid.uuid4())
correlation_id_ctx = contextvars.ContextVar("correlation_id", default=None)

def get_service_uuid():
    return service_uuid

def get_correlation_id():
    return correlation_id_ctx.get()

def set_correlation_id(corr_id=None):
    correlation_id_ctx.set(corr_id or str(uuid.uuid4()))
