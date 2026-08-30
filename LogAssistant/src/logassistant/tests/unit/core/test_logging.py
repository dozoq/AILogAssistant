import json

import pytest
import structlog
from logassistant.core.logging import setup_logging


@pytest.fixture
def reset_logger_state():
    yield
    structlog.reset_defaults()


def test_setup_logging_production_emits_valid_json(capsys, reset_logger_state):
    setup_logging(production=True)
    logger = structlog.get_logger()
    logger.info("test_event", foo="bar")

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["event"] == "test_event"
    assert payload["foo"] == "bar"
