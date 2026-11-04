import pytest

from app import create_app, db


@pytest.fixture
def app():
    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "JWT_SECRET_KEY": "test-jwt-secret-key-with-at-least-32-bytes",
        "SECRET_KEY": "test-secret-key-with-at-least-32-bytes",
    })
    with application.app_context():
        assert db.engine.url.database in (None, ":memory:")
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def create_account(client):
    counter = 0

    def create(name="Test User"):
        nonlocal counter
        counter += 1
        email = f"user{counter}@example.com"
        response = client.post("/api/auth/register", json={
            "nombre": name,
            "correo": email,
            "password": "ClaveSegura123",
        })
        assert response.status_code == 201
        login = client.post("/api/auth/login", json={
            "correo": email,
            "password": "ClaveSegura123",
        })
        return {"id": response.json["data"]["usuario"]["id_usuario"],
                "headers": {"Authorization": f"Bearer {login.json['data']['access_token']}"}}

    return create