from prometheus_client import Counter

TRACES_COLLECTED = Counter(
    "tracing_traces_collected_total", 
    "Total traces collected"
)

TRACES_EXPORTED = Counter(
    "tracing_traces_exported_total", 
    "Total traces exported"
)

TRACES_EXPORT_FAILED = Counter(
    "tracing_export_failed_total", 
    "Total trace export failures"
)

def record_trace_collected():
    TRACES_COLLECTED.inc()

def record_trace_exported():
    TRACES_EXPORTED.inc()

def record_trace_export_failed():
    TRACES_EXPORT_FAILED.inc()
