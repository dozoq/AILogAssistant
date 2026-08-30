from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile
from logassistant.domain import PolicyEngine, SecurityAgentService
from logassistant.schemas import GlobalSecurityPolicy, NetworkLogEntry
from logassistant.services import LogService


@pytest.fixture
def get_log_service():
    content = {
        "rules": [
            {
                "name": "SQL Injection Detection",
                "pattern": "(UNION\\s+SELECT|AND\\s+1=1|select\\+from)",
                "target_field": "url",
                "on_success_score": 100,
                "on_reject_score": 100,
                "type": "signature",
            },
            {
                "name": "WordPress Brute Force",
                "pattern": "/wp-login.php",
                "target_field": "url",
                "on_success_score": 150,
                "on_reject_score": 50,
                "type": "volumetric",
                "volumetric_threshold": 5,
            },
        ]
    }
    policy_object = GlobalSecurityPolicy.model_validate(content)
    policy_engine = PolicyEngine(policy_object)
    return LogService(policy_engine)


def test_log_service_constructor_success():
    content = {
        "rules": [
            {
                "name": "SQL Injection Detection",
                "pattern": "(UNION\\s+SELECT|AND\\s+1=1|select\\+from)",
                "target_field": "url",
                "on_success_score": 100,
                "on_reject_score": 100,
                "type": "signature",
            },
            {
                "name": "WordPress Brute Force",
                "pattern": "/wp-login.php",
                "target_field": "url",
                "on_success_score": 150,
                "on_reject_score": 50,
                "type": "volumetric",
                "volumetric_threshold": 5,
            },
        ]
    }
    policy_object = GlobalSecurityPolicy.model_validate(content)
    policy_engine = PolicyEngine(policy_object)
    service = LogService(policy_engine)
    assert isinstance(service.policy_engine, PolicyEngine)
    assert isinstance(service.agent, SecurityAgentService)


@pytest.mark.anyio
async def test_run_ai_analysis_success_call_dispatch(get_log_service):
    dispatch_mock = AsyncMock()
    ai_agent_mock = AsyncMock()
    with (
        patch(
            "logassistant.services.log_service.EventDispatcher.dispatch",
            new=dispatch_mock,
        ),
        patch(
            "logassistant.services.log_service.SecurityAgentService.analyze_log_entry",
            new=ai_agent_mock,
        ),
    ):
        await get_log_service.run_ai_analysis(
            "Brute Force", "1.1.1.1", "Log Details..."
        )
        dispatch_mock.assert_called_once()
        ai_agent_mock.assert_awaited_once_with(
            "Brute Force", "1.1.1.1", "Log Details..."
        )


@pytest.mark.anyio
async def test_run_analysis_success_trigger_ai():
    policy_engine_mock = MagicMock(spec=PolicyEngine)
    policy_engine_mock.evaluate_line.side_effect = [
        ("Brute Force", "Too many attempts", 85),
        None,
    ]

    service = LogService(policy_engine=policy_engine_mock)
    service.run_ai_analysis = AsyncMock()
    fake_file_content = b"1.1.1.1 - Login Failed\n2.2.2.2 - Login Success\n"
    fake_upload_file = UploadFile(file=BytesIO(fake_file_content), filename="test.log")

    async def read_in_chunks_mock(*args, **kwargs):
        yield fake_file_content

    with (
        patch(
            "logassistant.services.log_service.FileHandler.read_file_in_chunks",
            new=read_in_chunks_mock,
        ),
        patch(
            "logassistant.services.log_service.NetworkLogEntry.from_raw_line"
        ) as mock_from_raw_line,
    ):
        log_entry_mock_1 = MagicMock(spec=NetworkLogEntry, source_ip="1.1.1.1")
        log_entry_mock_2 = MagicMock(spec=NetworkLogEntry, source_ip="2.2.2.2")
        mock_from_raw_line.side_effect = [log_entry_mock_1, log_entry_mock_2]

        await service.run_analysis(fake_upload_file)

    assert policy_engine_mock.evaluate_line.call_count == 2

    service.run_ai_analysis.assert_called_once_with(
        "Brute Force",
        "1.1.1.1",
        details="Score:85, Reason: Too many attempts, Log:1.1.1.1 - Login Failed",
    )
