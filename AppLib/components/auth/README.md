# Auth & Secrets Subservices

## Overview

These subservices provide secure, centralized authentication and secrets management for your FastAPI platform.

- **/subservices/secrets**: Fetches sensitive config (JWT keys, Keycloak client secrets, etc.) from Vault.
- **/subservices/auth**: Validates JWTs (e.g., from Keycloak), using secrets managed by the secrets subservice.

## Features

- **No hardcoded secrets**: All sensitive data is retrieved from Vault.
- **Keycloak integration**: Validates Keycloak-issued JWTs using public keys.
- **Reusable**: Any subservice or API dependency can use these for secure token validation.

## Usage

### 1. Configure Vault and Keycloak

Set environment variables or config:

VAULT_ADDR=http://vault:8200
VAULT_TOKEN=your-vault-token
KEYCLOAK_SERVER_URL=https://keycloak.example.com/KEYCLOAK_CLIENT_ID=my-client
KEYCLOAK_REALM=myrealm
KEYCLOAK_VAULT_SECRET_PATH=secret/data/keycloak


### 2. Use the Dependency in Routers

from fastapi import APIRouter, Depends from api.dependencies import get_current_user

router = APIRouter()
async def protected_route(user=Depends(get_current_user)):
  return {“message”: f”Hello, {user.get(‘preferred_username’, ‘user’)}!”}


## Best Practices

- **Rotate secrets and client credentials regularly in Vault**
- **Secure all internal traffic with mTLS**
- **Monitor authentication failures and Vault access logs**
- **Never hardcode secrets in code or config files**

## References

- [Keycloak Python SDK](https://pypi.org/project/python-keycloak/)
- [hvac (HashiCorp Vault client)](https://pypi.org/project/hvac/)
- [Vault-Keycloak OIDC Integration](https://cfreeman.cloud/vault-keycloak-integration-with-oidc/)
- [FastAPI Security Docs](https://fastapi.tiangolo.com/tutorial/security/)

---

**This setup is production-ready, secure, and extensible for all your microservices.**
