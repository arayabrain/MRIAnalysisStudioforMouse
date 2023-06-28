import json
import pytest
from fastapi.testclient import TestClient
from backend.routers.auth import router

client = TestClient(router)


def test_register(monkeypatch):
    def mock(*args, **kwargs):
        return {
            "id": "lhJOxYjLVITaB2O0EeqP8mzltjb2",
            "email": "test@reactplus.jp",
            "display_name": None,
        }

    monkeypatch.setattr(client, "post", mock)
    response = client.post(
        "/auth/register",
        json={'email': 'test@reactplus.jp', 'password': 'test123@reactplus.jp'},
    )
    assert response['id'] == 'lhJOxYjLVITaB2O0EeqP8mzltjb2'


def test_login(monkeypatch):
    def mock(*args, **kwargs):
        return {
            "access_token": "test_access_token",
            "refresh_token": None,
            "token_type": "bearer",
        }

    monkeypatch.setattr(client, "post", mock)
    response = client.post(
        "/auth/login",
        json={'email': 'test@reactplus.jp', 'password': 'test123@reactplus.jp'},
    )
    assert response['access_token'] == 'test_access_token'
