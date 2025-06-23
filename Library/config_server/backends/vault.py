# config_server/backends/vault.py
import hvac
from os import getenv

class VaultSecretBackend:
    def __init__(self, vault_addr: str):
        self.client = hvac.Client(url=vault_addr)
        
    async def connect(self):
        if not self.client.is_authenticated():
            # Use Kubernetes service account token in production
            self.client.auth.approle.login(
                role_id=getenv("VAULT_ROLE_ID"),
                secret_id=getenv("VAULT_SECRET_ID")
            )
    
    async def get_secret(self, path: str) -> str:
        """Retrieve secret from Vault"""
        response = self.client.secrets.kv.v2.read_secret_version(path=path)
        return response["data"]["data"]["value"]
