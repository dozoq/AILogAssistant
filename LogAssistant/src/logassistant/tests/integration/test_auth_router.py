from fastapi.testclient import TestClient
from logassistant.app import app
import pytest

def test_auth_endpoint_success(client: TestClient, monkeypatch):
    monkeypatch.setenv("INTERNAL_CLIENT_SECRET", "correct-secret")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-key")
    response = client.post(
        "/auth/token",
        data={"grant_type": "client_credentials", "client_secret": "correct-secret"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"] != ""

def test_auth_endpoin_wrong_token(client :TestClient, monkeypatch):
    monkeypatch.setenv("INTERNAL_CLIENT_SECRET", "correct-secret")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-key")
    response = client.post(
        "/auth/token",
        data={"grant_type": "client_credentials", "client_secret": "bad-secret"},
    )

    assert response.status_code == 400

