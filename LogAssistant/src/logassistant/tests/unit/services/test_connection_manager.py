from unittest.mock import AsyncMock

import pytest
from fastapi import WebSocket
from logassistant.services.connection_manager import ConnectionManager


@pytest.fixture
def get_connection_manager():
    return ConnectionManager()


@pytest.mark.anyio
async def test_connection_manager_connection_success(
    get_connection_manager: ConnectionManager,
):
    ws = AsyncMock(spec=WebSocket)
    await get_connection_manager.connect(ws)
    ws.accept.assert_awaited_once()
    assert len(get_connection_manager.active_connections) == 1


@pytest.mark.anyio
async def test_connection_manager_disconnect(get_connection_manager: ConnectionManager):
    ws = AsyncMock(spec=WebSocket)
    await get_connection_manager.connect(ws)
    ws.accept.assert_awaited_once()
    get_connection_manager.disconnect(ws)
    assert len(get_connection_manager.active_connections) == 0
