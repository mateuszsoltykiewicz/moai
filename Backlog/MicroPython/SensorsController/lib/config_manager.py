import ujson

CONFIG_FILE = "config.json"
FACTORY_CONFIG_FILE = "factory_config.json"
LOG_FILE = "logs/events.log"

def log_event(event_type, details):
    try:
        with open(LOG_FILE, "a") as f:
            f.write('{}: {}\n'.format(event_type, details))
    except Exception:
        pass

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            config = ujson.load(f)
        validate_config(config)
        return config
    except Exception as e:
        log_event("CONFIG_ERROR", f"Failed to load config: {e}")
        with open(FACTORY_CONFIG_FILE) as f:
            config = ujson.load(f)
        validate_config(config)
        with open(CONFIG_FILE, "w") as f2:
            ujson.dump(config, f2)
        log_event("CONFIG_RECOVERY", "Restored factory config")
        return config

def save_config(new_config):
    validate_config(new_config)
    with open(CONFIG_FILE, "w") as f:
        ujson.dump(new_config, f)

def validate_config(config):
    assert "sensors" in config
    assert "canbus" in config
    assert "api_token" in config and len(config["api_token"]) >= 8
