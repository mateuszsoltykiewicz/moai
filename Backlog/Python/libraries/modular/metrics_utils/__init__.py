# /Python/libraries/modular/metrics_utils/__init__.py
def validate_metric(metric, config):
    # Validate metric against config (e.g., type, range, schema)
    if metric['name'] not in config['allowed_metrics']:
        raise ValueError("Metric not allowed")
    # Additional validation logic here
