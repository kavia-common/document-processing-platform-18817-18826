import os
from datetime import timedelta


class Config:
    """
    Base configuration. Uses environment variables for secrets and database.
    """
    # Flask basics
    PROPAGATE_EXCEPTIONS = True
    JSON_SORT_KEYS = False

    # OpenAPI
    API_TITLE = "Intelligent Receipt Processing API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/docs"
    OPENAPI_SWAGGER_UI_PATH = ""
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # JWT/Auth settings
    SECRET_KEY = os.environ.get("APP_SECRET_KEY", "change-me-in-production")
    ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get("ACCESS_TOKEN_EXPIRES_HOURS", "8")))
    REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get("REFRESH_TOKEN_EXPIRES_DAYS", "7")))
    PASSWORD_HASH_ROUNDS = int(os.environ.get("PASSWORD_HASH_ROUNDS", "12"))

    # Database (MySQL) via SQLAlchemy URI: mysql+pymysql://user:pass@host:port/db
    SQLALCHEMY_DATABASE_URI = os.environ.get("MYSQL_SQLALCHEMY_URL", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": int(os.environ.get("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "10")),
    }

    # Storage
    STORAGE_ROOT = os.environ.get("STORAGE_ROOT", "storage")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_MB", "25")) * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "tiff", "bmp", "gif", "heic", "webp"}

    # CORS origins
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # OCR provider configuration placeholders
    OCR_PROVIDER = os.environ.get("OCR_PROVIDER", "tesseract")  # or "aws_textract", "gcv", etc.
    # Additional provider-specific envs should be added as needed


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_MYSQL_SQLALCHEMY_URL", "sqlite:///:memory:")
    STORAGE_ROOT = "storage_test"


def get_config():
    env = os.environ.get("FLASK_ENV", "production").lower()
    if env in ("test", "testing", "ci"):
        return TestConfig
    return Config
