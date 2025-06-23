import pytest
from unittest.mock import patch, AsyncMock
from AppLib.components.secrets.manager import SecretsManager, VaultConfig

@pytest.fixture
def vault_config():
    return VaultConfig(
        address="https://vault.example.com",
        token="fake-token",
        secrets_path="secret/data/app",
        verify_ssl=False
    )

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_fetch_secret_success(mock_get, vault_config):
    # Mock Vault response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "data": {
            "data": {"username": "user", "password": "pass"}
        }
    })
    mock_get.return_value.__aenter__.return_value = mock_response

    async with SecretsManager(vault_config) as manager:
        secret = await manager.fetch_secret("database")
        assert secret == {"username": "user", "password": "pass"}

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_fetch_secret_failure(mock_get, vault_config):
    # Mock Vault error response
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_get.return_value.__aenter__.return_value = mock_response

    async with SecretsManager(vault_config) as manager:
        with pytest.raises(Exception):
            await manager.fetch_secret("database")

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_rotate_secret(mock_get, vault_config):
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "data": {
            "data": {"key": "value"}
        }
    })
    mock_get.return_value.__aenter__.return_value = mock_response

    async with SecretsManager(vault_config) as manager:
        await manager.rotate_secret("database")
        secret = await manager.fetch_secret("database")
        assert secret == {"key": "value"}

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_get_all_secrets(mock_get, vault_config):
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "data": {
            "data": {
                "secret1": "value1",
                "secret2": "value2"
            }
        }
    })
    mock_get.return_value.__aenter__.return_value = mock_response

    async with SecretsManager(vault_config) as manager:
        secrets = await manager.get_all_secrets()
        assert secrets == {"secret1": "value1", "secret2": "value2"}
