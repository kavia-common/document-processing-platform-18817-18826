import io
import os
import shutil
import tempfile
from typing import Dict

import pytest
from flask import Flask

# Ensure FLASK_ENV is set to test so TestConfig applies (in-memory SQLite, test storage)
os.environ.setdefault("FLASK_ENV", "test")

# Import the Flask app from the backend
from app import app as flask_app  # type: ignore
from app.models import db  # type: ignore
from app.models import seed_admin_if_missing  # type: ignore


@pytest.fixture(scope="session")
def app() -> Flask:
    """
    Provide the Flask app configured for testing.

    - Uses TestConfig (in-memory SQLite, storage_test root).
    - Creates all DB tables and yields the app for tests.
    """
    # Ensure a clean storage root for the session
    tmp_storage = tempfile.mkdtemp(prefix="storage_test_")
    flask_app.config["STORAGE_ROOT"] = tmp_storage
    flask_app.config["TESTING"] = True

    with flask_app.app_context():
        db.drop_all()
        db.create_all()
    yield flask_app

    # Cleanup after test session
    shutil.rmtree(tmp_storage, ignore_errors=True)


@pytest.fixture()
def client(app: Flask):
    """
    Flask test client fixture.
    """
    return app.test_client()


@pytest.fixture()
def db_session(app: Flask):
    """
    SQLAlchemy session fixture; ensures clean state per test where needed.
    """
    with app.app_context():
        yield db.session
        # Rollback any uncommitted work between tests
        db.session.rollback()


@pytest.fixture()
def register_user_and_get_token(client) -> Dict[str, str]:
    """
    Helper fixture to register a new user and return token and email/password.
    """
    email = "user@example.com"
    password = "secret"
    name = "User"
    reg_resp = client.post(
        "/auth/register",
        json={"email": email, "password": password, "name": name},
    )
    assert reg_resp.status_code in (201, 400)
    if reg_resp.status_code == 400:
        # Already exists; just login
        login_resp = client.post("/auth/login", json={"email": email, "password": password})
        assert login_resp.status_code == 200
        token = login_resp.get_json()["access_token"]
    else:
        token = reg_resp.get_json()["access_token"]
    return {"token": token, "email": email, "password": password}


@pytest.fixture()
def auth_header(register_user_and_get_token):
    """
    Authorization header dict for the registered user.
    """
    return {"Authorization": f"Bearer {register_user_and_get_token['token']}"}


@pytest.fixture()
def make_file_bytes():
    """
    Returns a factory that creates an in-memory bytes file for upload tests.
    """
    def _factory(content: bytes = b"Sample receipt total $12.34", filename: str = "receipt.txt"):
        return (io.BytesIO(content), filename)
    return _factory


@pytest.fixture()
def ensure_admin(db_session):
    """
    Seed an admin user into the test database if missing. Returns admin token via login.
    """
    email = "admin@example.com"
    password = "adminpass"
    # Seed admin if missing
    seed_admin_if_missing(db_session, email=email, password=password)
    return {"email": email, "password": password}
