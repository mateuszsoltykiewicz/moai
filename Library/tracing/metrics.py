from prometheus_client import Counter, Histogram

TRACES_COLLECTED = Counter("traces_collected_total", "Total traces collected")
TRACES_EXPORTED = Counter("traces_exported_total", "Total traces exported")
TRACES_EXPORT_FAILED = Counter("traces_export_failed_total", "Total trace export failures")
TRACE_PROCESSING_LATENCY = Histogram("trace_processing_latency_seconds", "Trace processing latency")

def record_trace_collected():
    TRACES_COLLECTED.inc()

def record_trace_exported():
    TRACES_EXPORTED.inc()

def record_trace_export_failed():
    TRACES_EXPORT_FAILED.inc()
