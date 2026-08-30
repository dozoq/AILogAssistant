from unittest.mock import AsyncMock

import pytest
from langchain_core.messages.ai import AIMessage
from logassistant.domain.security_agent import SecurityAgentService


@pytest.fixture
def get_security_agent() -> SecurityAgentService:
    return SecurityAgentService()


def test_security_agent_construction():
    security_agent = SecurityAgentService()
    assert "get_ip_activity_history" in security_agent.tools_map
    assert "get_mitre_knowledge_base" in security_agent.tools_map
    assert security_agent.llm is not None
    assert security_agent.output_parser is not None
    rendered = security_agent.prompt_template.format_messages(
        attack_type="Brute Force",
        ip="1.1.1.1",
        log_entry="...",
        format_instructions="...",
        chat_history=[],
    )
    assert rendered[0].type == "system"
    assert rendered[-1].type == "human"


@pytest.mark.anyio
async def test_analyze_log_retry_if_tool_call_until_error(
    get_security_agent: SecurityAgentService, monkeypatch
):
    fake_llm = AsyncMock()
    fake_llm.ainvoke = AsyncMock(
        side_effect=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_ip_activity_history",
                        "args": {"ip": "1.1.1.1"},
                        "id": "1",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_ip_activity_history",
                        "args": {"ip": "1.1.1.1"},
                        "id": "1",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_ip_activity_history",
                        "args": {"ip": "1.1.1.1"},
                        "id": "1",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_ip_activity_history",
                        "args": {"ip": "1.1.1.1"},
                        "id": "1",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_ip_activity_history",
                        "args": {"ip": "1.1.1.1"},
                        "id": "1",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_ip_activity_history",
                        "args": {"ip": "1.1.1.1"},
                        "id": "1",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_ip_activity_history",
                        "args": {"ip": "1.1.1.1"},
                        "id": "1",
                    }
                ],
            ),
        ]
    )
    monkeypatch.setattr(get_security_agent, "llm_with_tools", fake_llm)
    result = await get_security_agent.analyze_log_entry("Brute Force", "1.1.1.1", "...")
    assert result == {
        "error": "Failed to generate a valid response after multiple attempts."
    }


@pytest.mark.anyio
async def test_analyze_log_entry_returns_final_message_if_no_tool_call(
    get_security_agent: SecurityAgentService, monkeypatch
):
    fake_llm = AsyncMock()
    fake_llm.ainvoke = AsyncMock(
        side_effect=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_ip_activity_history",
                        "args": {"ip": "1.1.1.1"},
                        "id": "1",
                    }
                ],
            ),
            AIMessage(content='{"raport": "..."}'),
        ]
    )
    monkeypatch.setattr(get_security_agent, "llm_with_tools", fake_llm)
    result = await get_security_agent.analyze_log_entry("Brute Force", "1.1.1.1", "...")
    assert "raport" in result
