from Library.vault import VaultManager
from Library.logging import get_logger
from .schemas import SecretRotateRequest, SecretRotateResponse

logger = get_logger(__name__)

class SecretsRotatorManager:
    @staticmethod
    async def setup():
        await VaultManager.setup()
        logger.info("SecretsRotatorManager setup complete.")

    @staticmethod
    async def shutdown():
        await VaultManager.shutdown()
        logger.info("SecretsRotatorManager shutdown complete.")

    @staticmethod
    async def rotate_secret(req: SecretRotateRequest) -> SecretRotateResponse:
        # Example: rotate secret in Vault
        new_secret = await VaultManager.rotate_secret(req.path)
        logger.info(f"Secret rotated for {req.path}")
        return SecretRotateResponse(path=req.path, new_version=new_secret["version"])
