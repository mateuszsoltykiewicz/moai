# Secrets Manager

Asynchronous, production-ready secrets manager for AppLib.

## Features

- **Vault KV v2 integration:** Async, with in-memory caching
- **Token renewal:** Auto-refreshes Vault token in background
- **Fallbacks:** Loads secrets from environment or local JSON if Vault is unavailable
- **Dynamic DB credentials:** Fetches from Vault's database engine
- **Rotation notification:** Register a callback for hot-reloading on secret rotation

## Extra Features

### Token Renewal

- The manager will periodically renew its Vault token (if allowed).
- If renewal fails, logs an error and can trigger a callback for alerting or shutdown.

### Fallbacks

- If Vault is unavailable, secrets can be loaded from environment variables or a local encrypted JSON file.
- This is useful for local development and CI/CD.

### Multiple Secret Engines

- Supports fetching secrets from different Vault engines (KV, database, AWS, PKI, etc.).
- Add your own fetch methods for new engines as needed.

### Rotation Notification

- Register a callback to be notified when a secret is rotated.
- Use this to hot-reload connections in other services.


## Usage Example
from AppLib.services.secrets.manager import SecretsManager, VaultConfig

vault_cfg = VaultConfig(
  address=“https://vault.example.com”,
  token=“s.xxxxxxxx”,
  secrets_path=“secret/data/app”,
  verify_ssl=True,
  fallback_json=“configs/dev/fallback_secrets.json”
)

async def on_secret_rotated(key, secret):
  print(f”Secret {key} rotated, new value: {secret}”)

async with SecretsManager(vault_cfg, on_rotate=on_secret_rotated) as secrets:
  await secrets.start()
  db_creds = await secrets.fetch_secret(“database”)
  kafka_creds = await secrets.fetch_secret(“kafka”)
  await secrets.rotate_secret(“database”)
  dynamic_creds = await secrets.fetch_dynamic_db_creds(“my-role”)
  await secrets.stop()

---


## Usage

from AppLib.services.secrets.manager import SecretsManager, VaultConfig

vault_cfg = VaultConfig(
  address=“https://vault.example.com”,
  token=“s.xxxxxxxx”,
  secrets_path=“secret/data/app”,
  verify_ssl=True

)
async with SecretsManager(vault_cfg) as secrets:
  db_creds = await secrets.fetch_secret(“database”)
  kafka_creds = await secrets.fetch_secret(“kafka”)


## Best Practices

- Store your Vault token securely (not in source code).
- Rotate tokens and secrets regularly.
- Use bulk loading (`get_all_secrets`) at startup for performance.
- Always close the session (`await secrets.close()`) on shutdown.
- Use Vault tokens with short TTL and enable auto-renewal.
- Store fallback secrets securely for dev/CI only.
- Use the rotation callback to hot-reload DB/Kafka clients on secret change.

## Testing

- Use mocks for Vault HTTP responses.
- Test fallback and rotation logic.

---

