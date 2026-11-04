from app import create_app, db
from app.models import Usuario


def test_sqlite_data_survives_app_recreation(tmp_path):
    database_path = tmp_path / "persistent.db"
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path.as_posix()}",
        "JWT_SECRET_KEY": "test-jwt-secret-key-with-at-least-32-bytes",
        "SECRET_KEY": "test-secret-key-with-at-least-32-bytes",
    }
    first_app = create_app(config)
    with first_app.app_context():
        db.create_all()
        user = Usuario(nombre="Persistente", correo="persistente@example.com")
        user.establecer_password("ClaveSegura123")
        db.session.add(user)
        db.session.commit()

    second_app = create_app(config)
    with second_app.app_context():
        stored_user = Usuario.query.filter_by(correo="persistente@example.com").one()
        assert stored_user.nombre == "Persistente"
        assert stored_user.verificar_password("ClaveSegura123")