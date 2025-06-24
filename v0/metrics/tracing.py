from prometheus_client import Counter, Histogram
from utils.prometheus_instrumentation import REGISTRY
from opentelemetry import trace

TRACES_STARTED = Counter(
    "tracing_api_traces_started_total",
    "Total traces started in the API",
    registry=REGISTRY
)
TRACES_COMPLETED = Counter(
    "tracing_api_traces_completed_total",
    "Total traces completed in the API",
    registry=REGISTRY
)
TRACING_ERRORS = Counter(
    "tracing_api_errors_total",
    "Total errors encountered in tracing API",
    registry=REGISTRY
)
SPAN_DURATION = Histogram(
    "tracing_api_span_duration_seconds",
    "Duration of traced spans in the API",
    buckets=[0.01, 0.05, 0.1, 0.3, 1, 2.5, 5, 10],
    registry=REGISTRY
)

def observe_span_duration(start_time, end_time):
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, "032x")
    SPAN_DURATION.observe(end_time - start_time, exemplar={"TraceID": trace_id})
