import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from sqlalchemy import event
from sqlalchemy.engine import Engine

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(connection, _record):
    if connection.__class__.__module__.startswith("sqlite3"):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(test_config=None):
    app = Flask(__name__)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.from_object(Config)
    if test_config:
        app.config.from_mapping(test_config)

    if app.config["APP_ENV"] == "production":
        secret_key = app.config["SECRET_KEY"]
        jwt_secret_key = app.config["JWT_SECRET_KEY"]
        known_defaults = {
            "dev-only-secret-key-change-before-deploy-01",
            "dev-only-jwt-secret-key-change-before-deploy-01",
            "replace-with-a-long-random-secret",
            "replace-with-another-long-random-secret",
        }
        if (
            not isinstance(secret_key, str)
            or not isinstance(jwt_secret_key, str)
            or len(secret_key) < 32
            or len(jwt_secret_key) < 32
            or secret_key == jwt_secret_key
            or secret_key in known_defaults
            or jwt_secret_key in known_defaults
            or secret_key.startswith("replace-with-")
            or jwt_secret_key.startswith("replace-with-")
        ):
            raise RuntimeError("Production requires two distinct random secrets of at least 32 characters")

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    from app import models
    from app.models import RevokedToken
    from app.routes import api

    app.register_blueprint(api, url_prefix="/api")

    @jwt.token_in_blocklist_loader
    def token_is_revoked(_header, payload):
        return RevokedToken.query.filter_by(jti=payload["jti"]).first() is not None

    from app.utils.responses import failure
    from app.utils.validators import ValidationError

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        db.session.rollback()
        return failure(str(error), error.status, error.errors)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(_error):
        db.session.rollback()
        return failure("El registro entra en conflicto con información existente", 409)

    @jwt.unauthorized_loader
    def missing_token(_reason):
        return failure("Se requiere autenticación", 401)

    @jwt.invalid_token_loader
    def invalid_token(_reason):
        return failure("El token de autenticación no es válido", 401)

    @jwt.expired_token_loader
    def expired_token(_header, _payload):
        return failure("La sesión ha expirado", 401)

    @jwt.revoked_token_loader
    def revoked_token(_header, _payload):
        return failure("La sesión ha sido revocada", 401)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"success": False, "message": "Recurso no encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "mensaje": "Bienvenido a FINTRACK API",
            "estado": "funcionando",
            "version": "1.0.0",
        }), 200

    return app