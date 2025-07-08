# Config Server Component

## Overview

Centralized configuration management server with Git-backed versioning and Vault secrets integration. Provides dynamic configuration updates to microservices via WebSocket notifications.

## Features

- **Git Versioning**: Tracks configuration changes with commit history
- **Vault Integration**: Secure secret management
- **WebSocket Notifications**: Real-time config updates to services
- **Caching**: Optimized config retrieval with cache invalidation
- **Metrics**: Tracks operations and fetch times
- **Centralized Logging**: Uses `Library.logging` component
- **JWT Security**: Secures HTTP and WebSocket endpoints

## Key Components

| Component         | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `GitConfigBackend`| Fetches and watches config from Git repository                          |
| `VaultSecretBackend` | Resolves secrets from HashiCorp Vault                               |
| `ConfigServer`    | Core server managing config retrieval and notifications                 |
| `ConfigClient`    | Client for services to fetch config and receive updates                |
| `ConfigChangeNotifier` | WebSocket-based change notification system                      |

## Security

- **JWT/OIDC Validation**: All HTTP and WebSocket requests require valid tokens
- **Vault Authentication**: Uses AppRole for secure secret access
- **RBAC Enforcement**: Requires `config:read` for clients, `config:write` for admins

## Usage Example

Server setup

server = ConfigServer(
repo_url="https://github.com/your/config-repo",
vault_addr="https://vault.example.com",
metrics_manager=metrics_manager
)
await server.start()
Client usage

client = ConfigClient(
config_server_url="http://config-server:8000",
service_name="payment-service",
env="production",
auth_token="<JWT>"
)
await client.fetch_initial_config()
await client.start_listening()


## Interactions

- **Git Repository**: For versioned configuration storage
- **Vault**: For secret resolution
- **Library.api.security**: For JWT validation
- **Library.metrics**: For operation metrics
- **All Microservices**: Consume configuration through clients

## Potential Improvements

- Add configuration history and rollback capabilities
- Implement configuration diffing for partial updates
- Add audit logging for configuration changes

## Potential Bug Sources

1. **Git Connectivity**: Network issues may prevent config updates
2. **Secret Resolution**: Vault unavailability breaks config loading
3. **Cache Invalidation**: May not detect all service dependencies
4. **WebSocket Scalability**: High connection counts may cause resource exhaustion

## Security Best Practices

- Rotate Vault AppRole credentials regularly
- Use short-lived JWTs for client connections
- Restrict Git repository access
- Encrypt sensitive configuration values

## Logging

All operations use `Library.logging` with structured JSON format. Sensitive data (secrets) is never logged.
