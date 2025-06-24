# adapters/tracing.py

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from opentelemetry import trace
from opentelemetry.trace import Span
from metrics.tracing import (
    TRACING_SPANS_STARTED,
    TRACING_SPANS_COMPLETED,
    TRACING_ERRORS,
    TRACING_SPAN_DURATION,
)

class AsyncTracingAdapter:
    def __init__(self, tracer: Optional[trace.Tracer] = None):
        self.tracer = tracer or trace.get_tracer("adapters.tracing")

    @asynccontextmanager
    async def start_span(self, name: str, **kwargs) -> AsyncGenerator[Span, None]:
        """Async context manager for tracing spans with metrics."""
        TRACING_SPANS_STARTED.inc()
        start_time = time.time()
        span = None
        try:
            with self.tracer.start_as_current_span(name, **kwargs) as _span:
                span = _span
                yield span
            TRACING_SPANS_COMPLETED.inc()
        except Exception:
            TRACING_ERRORS.inc()
            raise
        finally:
            duration = time.time() - start_time
            TRACING_SPAN_DURATION.observe(duration)

    def get_current_trace_id(self) -> str:
        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx and ctx.trace_id:
            return format(ctx.trace_id, "032x")
        return ""