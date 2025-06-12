# adapters/tracing.py
from opentelemetry import trace
from metrics.tracing import TRACING_SPANS_STARTED, TRACING_SPANS_COMPLETED, TRACING_ERRORS, TRACING_SPAN_DURATION
import time

class AsyncTracingAdapter:
    def __init__(self, tracer=None):
        self.tracer = tracer or trace.get_tracer("adapters.tracing")

    async def start_span(self, name: str, **kwargs):
        TRACING_SPANS_STARTED.inc()
        start_time = time.time()
        try:
            # Async context manager for span
            with self.tracer.start_as_current_span(name, **kwargs) as span:
                yield span  # Usage: async with adapter.start_span("name") as span:
            TRACING_SPANS_COMPLETED.inc()
        except Exception:
            TRACING_ERRORS.inc()
            raise
        finally:
            TRACING_SPAN_DURATION.observe(time.time() - start_time)

    def get_current_trace_id(self) -> str:
        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx and ctx.trace_id:
            return format(ctx.trace_id, "032x")
        return ""
