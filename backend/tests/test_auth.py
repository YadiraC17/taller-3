from datetime import timedelta

import pytest

from flask_jwt_extended import create_access_token

from app import create_app
from app.config import normalize_database_url


def test_register_and_login(client):
    registered = client.post("/api/auth/register", json={
        "nombre": "Ana Demo",
        "correo": "ana@example.com",
        "password": "ClaveSegura123",
    })
    assert registered.status_code == 201
    assert "password_hash" not in registered.json["data"]["usuario"]

    response = client.post("/api/auth/login", json={
        "correo": "ana@example.com",
        "password": "ClaveSegura123",
    })
    assert response.status_code == 200
    assert response.json["data"]["access_token"]


def test_duplicate_email_returns_conflict(client):
    data = {"nombre": "Ana", "correo": "ana@example.com", "password": "ClaveSegura123"}
    assert client.post("/api/auth/register", json=data).status_code == 201
    assert client.post("/api/auth/register", json=data).status_code == 409


def test_private_endpoint_requires_token(client):
    response = client.get("/api/transacciones")
    assert response.status_code == 401
    assert response.json["success"] is False


def test_private_endpoint_rejects_invalid_token(client):
    response = client.get("/api/transacciones", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
    assert response.json["success"] is False


def test_private_endpoint_rejects_expired_token(client, app):
    with app.app_context():
        token = create_access_token(identity="1", expires_delta=timedelta(seconds=-1))
    response = client.get("/api/transacciones", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json["success"] is False


def test_logout_revokes_access_token(client, create_account):
    account = create_account()
    logout = client.post("/api/auth/logout", headers=account["headers"])

    assert logout.status_code == 200
    response = client.get("/api/auth/me", headers=account["headers"])
    assert response.status_code == 401
    assert response.json["success"] is False


def test_production_rejects_example_secrets():
    with pytest.raises(RuntimeError, match="Production requires"):
        create_app({
            "APP_ENV": "production",
            "SECRET_KEY": "replace-with-a-long-random-secret",
            "JWT_SECRET_KEY": "replace-with-another-long-random-secret",
        })


@pytest.mark.parametrize(
    ("database_url", "expected"),
    [
        (
            "postgres://user:pass@host/db?sslmode=require",
            "postgresql+psycopg://user:pass@host/db?sslmode=require",
        ),
        (
            "postgresql://user:pass@host/db?sslmode=require",
            "postgresql+psycopg://user:pass@host/db?sslmode=require",
        ),
        ("sqlite:///fintrack.db", "sqlite:///fintrack.db"),
    ],
)
def test_normalize_database_url(database_url, expected):
    assert normalize_database_url(database_url) == expected