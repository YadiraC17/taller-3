import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-before-deploy-01")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-jwt-secret-key-change-before-deploy-01")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "..", "instance", "fintrack.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 12
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500"
    ).split(",")
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS if origin.strip()]