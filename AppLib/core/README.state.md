# Application State Management

## Configuration

| Environment Variable | Default               | Description                  |
|----------------------|-----------------------|------------------------------|
| `STATE_PATH`         | `state_backups/...`   | State file path              |
| `BACKUP_INTERVAL`    | 300                   | Backup interval in seconds   |

## Usage



## Features
- **Thread-safe async access** using asyncio locks
- **Persistence** with automatic backups
- **Validation** via Pydantic models
- **Integration** with secrets management and config
- **Partial updates** for efficient state modifications

## Usage

from AppLib.core.state import AppState

Initialize on application startup
state = AppState() await state.initialize(config)

Initialize with encryption
state = AppState()
  state.configure_encryption(b”your-32-byte-encryption-key”)
  await state.initialize()

Update state
await state.update_state(
  {
    “service_ready”: True,
    “metrics”: {“requests”: 42}
  },
  persist=True
)

Add listener
async def log_change(new_state):
  logger.info(“State changed: %s”, new_state)
  state.add_listener(log_change)

Access state
current_state = await state.get_state()
print(current_state.service_ready)

Update state
await state.update_state({“service_ready”: True}, persist=True)

Automatic backups
await state.start_auto_backup(interval=300)  # 5 minutes

## State Versioning

- The state file contains a `version` field.
- If the version does not match, the system logs a warning and can perform migrations.


## Migration Guide
1. Update `AppStateModel` with new fields
2. Implement migration logic in `migrate_state()`
3. Update version number


### Version Migration
1. Bump the `version` field in `AppStateModel`
2. Implement migration logic in `migrate_state()`
3. Test with old state files

Example migration call
await state.migrate_state(target_version=2)


### Encryption Management
1. Generate key: `Fernet.generate_key()`
2. Store securely (e.g., in Vault)
3. Inject during service initialization:

secrets = SecretsManager(config)
key = await secrets.get_encryption_key()
state.set_encryption_key(key)

### Backup Strategies
- **Scheduled Backups:** Use `start_auto_backup()`
- **On-Demand Backups:** Call `_persist_state()`
- **Encrypted Backups:** Enable via `set_encryption_key()`

## Testing Guide

Run all tests
pytest tests/integration/test_state.py -v

Test specific features
pytest tests/integration/test_state.py -k “test_encrypted_persistence”

## State Encryption

- State files can be encrypted using Fernet symmetric encryption.
- Store the encryption key securely (e.g., in Vault).
- Set the key at runtime:

state.set_encryption_key(b”your-fernet-key-here”)


## Integration Testing

- See `tests/integration/test_state.py` for persistence and restore tests.


## State Schema

| Field           | Type          | Description                      |
|-----------------|---------------|----------------------------------|
| service_ready   | bool          | Overall system readiness         |
| last_backup     | datetime      | Timestamp of last backup         |
| connections     | dict          | Service connection statuses      |
| metrics         | dict          | System performance metrics       |
| hardware_status | dict          | I2C/CANBus device statuses       |
| custom_state    | dict          | Service-specific state extensions|

## Best Practices
1. Use partial updates for better performance
2. Enable automatic backups for critical state
3. Validate state changes through the Pydantic model
4. Access state through the singleton instance
5. Integrate state changes with event engine

---

