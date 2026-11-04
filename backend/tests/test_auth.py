from datetime import timedelta

from flask_jwt_extended import create_access_token


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