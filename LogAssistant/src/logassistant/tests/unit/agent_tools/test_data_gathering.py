from logassistant.agent_tools import get_ip_activity_history


def test_get_activity_history_success():
    assert len(get_ip_activity_history.invoke("1.1.1.1")) == 4
