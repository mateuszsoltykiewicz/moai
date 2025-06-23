from pydantic import BaseModel, Field
from .auth import KeycloakConfig, OAuthConfig
from .api import RoutersConfig
from .security import SecurityConfig
from .kafka import KafkaConfig
from .database import DatabaseConfig
from .state import PersistenceConfig
from .vault import VaultConfig

class AppConfig(BaseModel):
    kafka: KafkaConfig
    database: DatabaseConfig
    persistence: PersistenceConfig
    vault: VaultConfig
    keycloak: KeycloakConfig
    environment: str = Field(default="dev")
    routers: RoutersConfig = Field(default_factory=RoutersConfig)
    auth: OAuthConfig = Field(default_factory=OAuthConfig)
    security: SecurityConfig = SecurityConfig()

    class Config:
        schema_extra = {
            "example": {
                "kafka": {
                    "bootstrap_servers": "kafka:9092",
                    "group_id": "my-consumer-group",
                    "auto_offset_reset": "earliest",
                    "security_protocol": "PLAINTEXT",
                    "ssl_cafile": None,
                    "ssl_certfile": None,
                    "ssl_keyfile": None
                },
                "database": {
                    "host": "db",
                    "port": 5432,
                    "user": "dbuser",
                    "password": "default",
                    "database": "mydb"
                },
                "persistence": {
                    "enabled": True,
                    "path": "state_backups/latest_state.json"
                },
                "vault": {
                    "address": "http://vault:8200",
                    "token": "s.xxxxxxxx",
                    "secrets_path": "secret/data/myapp",
                    "verify_ssl": True,
                    "fallback_json": None
                },
                "keycloak": {
                    "server_url": "https://keycloak.example.com",
                    "client_id": "my-client",
                    "realm": "myrealm",
                    "vault_secret_path": "keycloak"
                },
                "environment": "dev",
                "routers": RoutersConfig.Config.schema_extra["example"],
                "auth": {
                    "enabled": True
                }
            }
        }


__all__ = [
    'AppConfig',
    'KafkaConfig',
    'DatabaseConfig',
    'VaultConfig',
    'KeycloakConfig',
    'OAuthConfig',
    'PersistenceConfig',
    'RoutersConfig',
    'SecurityConfig'
]
