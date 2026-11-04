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