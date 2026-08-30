from datetime import datetime, timedelta, timezone

import jwt
import pytest
from logassistant.core import BussinessException
from logassistant.services import AuthService


@pytest.fixture
def get_token(monkeypatch) -> str:
    monkeypatch.setenv("INTERNAL_CLIENT_SECRET", "correct-secret")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-key")
    return AuthService.authenticate_client("correct-secret")


def test_authenticate_client_success(monkeypatch):
    monkeypatch.setenv("INTERNAL_CLIENT_SECRET", "correct-secret")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-key")
    result: str = AuthService.authenticate_client("correct-secret")
    assert result != ""


def test_authenticate_client_wrong_secret(monkeypatch):
    monkeypatch.setenv("INTERNAL_CLIENT_SECRET", "correct-secret")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-key")

    with pytest.raises(BussinessException):
        AuthService.authenticate_client("bad-secret")


def test_verify_token_success(get_token: str):
    result = AuthService.verify_machine_token(get_token)
    assert "iss" in result
    assert "sub" in result
    assert "scope" in result
    assert "exp" in result


def test_verify_token_illegal_token_throw(monkeypatch):
    monkeypatch.setenv("INTERNAL_CLIENT_SECRET", "correct-secret")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-key")
    with pytest.raises(BussinessException):
        AuthService.verify_machine_token("aaa.bbb.ccc")


def test_verify_token_expired_token_throw(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test-key")

    expired_token = jwt.encode(
        {
            "sub": "logassistant-frontend",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        "test-key",
        algorithm="HS256",
    )
    with pytest.raises(BussinessException):
        AuthService.verify_machine_token(expired_token)
