import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


def allowed_file(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in set(current_app.config.get("ALLOWED_EXTENSIONS", []))


def compute_checksum(file_path: str, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _get_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret_key=current_app.config["SECRET_KEY"], salt="auth-token")


# PUBLIC_INTERFACE
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed access token string for a subject (user id or email)."""
    serializer = _get_serializer()
    # expires_delta is kept for API compatibility; URLSafeTimedSerializer uses max_age during decode.
    payload = {"sub": subject}
    token = serializer.dumps(payload)
    # Note: URLSafeTimedSerializer embeds timestamp; expiration checked on loads.
    return token


# PUBLIC_INTERFACE
def decode_access_token(token: str, max_age: Optional[int] = None) -> Tuple[bool, Optional[str]]:
    """Decode and validate an access token. Returns (is_valid, subject)."""
    serializer = _get_serializer()
    if max_age is None:
        delta = current_app.config.get("ACCESS_TOKEN_EXPIRES")
        max_age = int(delta.total_seconds()) if delta else 8 * 3600
    try:
        data = serializer.loads(token, max_age=max_age)
        return True, data.get("sub")
    except SignatureExpired:
        return False, None
    except BadSignature:
        return False, None
