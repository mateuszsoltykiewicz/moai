import json
from models.config import AppConfig

def test_appconfig_schema_sync():
    with open("schemas/validation/app_config.schema.json") as f:
        file_schema = json.load(f)
    model_schema = AppConfig.model_json_schema()
    assert file_schema == model_schema, "AppConfig schema out of sync!"
