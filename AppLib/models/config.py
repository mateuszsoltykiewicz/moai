"""
Pydantic schemas for application configuration.
Extend as needed for your environment.
"""

from pydantic import BaseModel, Field, SecretStr
from typing import Optional

class KafkaConfig(BaseModel):
    bootstrap_servers: str = Field(..., description="Kafka bootstrap servers")
    group_id: str = Field(..., description="Kafka consumer group ID")
    auto_offset_reset: str = Field(default="earliest", description="Kafka offset reset policy")
    security_protocol: Optional[str] = Field(default="PLAINTEXT")
    ssl_cafile: Optional[str]
    ssl_certfile: Optional[str]
    ssl_keyfile: Optional[str]

class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: SecretStr
    database: str

class PersistenceConfig(BaseModel):
    enabled: bool = Field(default=False)
    path: Optional[str] = Field(default="state_backups/latest_state.json")

class AuthConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable token authentication for API routers")

class RoutersConfig(BaseModel):
    """
    Configuration schema for enabling/disabling routers (API modules).
    """
    canbus: bool = Field(default=False, description="Enable CANBus API router")
    database: bool = Field(default=False, description="Enable Database API router")
    i2c: bool = Field(default=False, description="Enable I2C API router")
    kafka: bool = Field(default=False, description="Enable Kafka API router")
    alarms: bool = Field(default=True, description="Enable Alarms API router")
    appstate: bool = Field(default=True, description="Enable AppState API router")
    audit: bool = Field(default=True, description="Enable Audit API router")
    auth: bool = Field(default=True, description="Enable Auth API router")
    config: bool = Field(default=True, description="Enable Config API router")
    events: bool = Field(default=True, description="Enable Events API router")
    health: bool = Field(default=True, description="Enable Health API router")
    logging: bool = Field(default=True, description="Enable Logging API router")
    metrics: bool = Field(default=True, description="Enable Metrics API router")
    mtls: bool = Field(default=True, description="Enable mTLS API router")
    rate_limiting: bool = Field(default=True, description="Enable Rate Limiting API router")
    secrets: bool = Field(default=True, description="Enable Secrets API router")
    tracing: bool = Field(default=True, description="Enable Tracing API router")
    updates: bool = Field(default=True, description="Enable Updates API router")

    class Config:
        schema_extra = {
            "example": {
                "canbus": True,
                "database": False,
                "i2c": False,
                "kafka": True,
                "alarms": True,
                "appstate": True,
                "audit": True,
                "auth": True,
                "config": True,
                "events": True,
                "health": True,
                "logging": True,
                "metrics": True,
                "mtls": True,
                "rate_limiting": True,
                "secrets": True,
                "tracing": True,
                "updates": True
            }
        }

class VaultConfig(BaseModel):
    address: str
    token: str
    secrets_path: str
    verify_ssl: bool = True
    fallback_json: Optional[str] = None

class KeycloakConfig(BaseModel):
    server_url: str
    client_id: str
    realm: str
    vault_secret_path: str = "keycloak"  # Vault path for client_secret

class AppConfig(BaseModel):
    kafka: KafkaConfig
    database: DatabaseConfig
    persistence: PersistenceConfig
    vault: VaultConfig
    keycloak: KeycloakConfig
    environment: str = Field(default="dev")
    routers: RoutersConfig = Field(default_factory=RoutersConfig)

    class Config:
        schema_extra = {
            "example": {
                "routers": RoutersConfig.Config.schema_extra["example"],
                # ...other config sections...
            }
        }
