from lib.config_manager import load_config, log_event

def boot():
    config = load_config()
    log_event("SYSTEM_BOOT", "SensorsController booted with safe state")
    # Initialize sensors to safe state here if needed

boot()
