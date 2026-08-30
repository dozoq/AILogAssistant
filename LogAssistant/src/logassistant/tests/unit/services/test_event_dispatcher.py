from unittest.mock import AsyncMock, patch

import pytest
from logassistant.services import EventDispatcher


@pytest.mark.anyio
async def test_dispatcher_broadcast_success():
    with patch(
        "logassistant.services.connection_manager.connection_manager.broadcast",
        new=AsyncMock(),
    ):
        await EventDispatcher.dispatch(
            "BruteForce", "1.1.1.1", "Block ip 1.1.1.1", "Turn on firewall"
        )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "attack_type,ip,mitigation_plan,recomendations",
    [
        ("", "1.1.1.1", "Block ip 1.1.1.1", "Turn on firewall"),
        ("BruteForce", "", "Block ip 1.1.1.1", "Turn on firewall"),
        ("BruteForce", "1.1.1.1", "", "Turn on firewall"),
        ("BruteForce", "1.1.1.1", "Block ip 1.1.1.1", ""),
    ],
)
async def test_dispatcher_broadcast_empty(
    attack_type, ip, mitigation_plan, recomendations
):
    with pytest.raises(ValueError):
        await EventDispatcher.dispatch(attack_type, ip, mitigation_plan, recomendations)
