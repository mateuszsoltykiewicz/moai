# tests/test_state.py
import pytest
from unittest.mock import AsyncMock, patch
from core.state import AppState, StateManagementError

@pytest.fixture
async def state():
    state = AppState()
    await state.initialize()
    yield state
    await state.stop_auto_backup()

@pytest.mark.asyncio
async def test_state_initialization(state):
    current_state = await state.get_state()
    assert current_state.version == 1

@pytest.mark.asyncio
async def test_state_persistence(state, tmp_path):
    state._persistence_path = tmp_path / "test_state.json"
    await state.update_state({"service_ready": True}, persist=True)
    assert state._persistence_path.exists()
