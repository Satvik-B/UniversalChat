import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("services.auth.auth_service.AuthService.exchange_code_for_tokens")
@patch("services.auth.auth_service.AuthService.verify_id_token")
@patch("services.auth.auth_service.AuthService.store_user_in_firestore")
@patch("services.auth.auth_service.AuthService.issue_jwt")
def test_callback_success(mock_issue_jwt, mock_store_user, mock_verify_id, mock_exchange):
    mock_exchange.return_value = {"id_token": "fake-id-token"}
    mock_verify_id.return_value = {"sub": "123", "email": "test@example.com", "name": "Test User"}
    mock_issue_jwt.return_value = "jwt-token"
    response = client.get("/auth/callback?code=fakecode")
    assert response.status_code == 200
    assert response.json()["access_token"] == "jwt-token"
    mock_store_user.assert_called_once()

@patch("services.auth.auth_service.AuthService.exchange_code_for_tokens", side_effect=Exception("fail"))
def test_callback_failure(mock_exchange):
    response = client.get("/auth/callback?code=badcode")
    assert response.status_code == 400
    assert "fail" in response.json()["detail"]

def test_login_redirect():
    response = client.get("/auth/login", allow_redirects=False)
    assert response.status_code in (302, 307)
    assert "accounts.google.com" in response.headers["location"]

@patch("services.auth.auth_service.AuthService.extract_user_from_jwt")
def test_me_success(mock_extract):
    mock_extract.return_value = {"sub": "123", "email": "test@example.com"}
    headers = {"Authorization": "Bearer testtoken"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "test@example.com"

@patch("services.auth.auth_service.AuthService.extract_user_from_jwt", side_effect=Exception("bad token"))
def test_me_unauthorized(mock_extract):
    headers = {"Authorization": "Bearer badtoken"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401
    assert "bad token" in response.json()["detail"]
