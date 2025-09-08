from functools import wraps
from typing import Optional

from flask import request, g
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import func

from ..models import db, User
from ..schemas import UserRegisterSchema, UserLoginSchema, TokenSchema
from ..utils import create_access_token, decode_access_token

blp = Blueprint("Auth", "auth", url_prefix="/auth", description="Authentication endpoints")


def _get_token_from_header() -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1]
    return None


# PUBLIC_INTERFACE
def require_auth(fn):
    """Decorator that requires a valid Bearer token, sets g.current_user."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _get_token_from_header()
        if not token:
            abort(401, message="Missing Authorization header")
        valid, sub = decode_access_token(token)
        if not valid or not sub:
            abort(401, message="Invalid or expired token")
        user = db.session.query(User).filter(func.lower(User.email) == str(sub).lower()).first()
        if not user:
            abort(401, message="User not found")
        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper


@blp.route("/register")
class RegisterResource(MethodView):
    @blp.arguments(UserRegisterSchema, location="json")
    @blp.response(201, TokenSchema)
    def post(self, json_data):
        """
        Register a user and return an access token.
        """
        email = json_data["email"].strip().lower()
        if db.session.query(User).filter(func.lower(User.email) == email).first():
            abort(400, message="Email already in use")
        user = User(email=email, name=json_data.get("name"))
        user.set_password(json_data["password"])
        db.session.add(user)
        db.session.commit()
        token = create_access_token(subject=user.email)
        return {"access_token": token}


@blp.route("/login")
class LoginResource(MethodView):
    @blp.arguments(UserLoginSchema, location="json")
    @blp.response(200, TokenSchema)
    def post(self, json_data):
        """
        Login and obtain access token.
        """
        email = json_data["email"].strip().lower()
        password = json_data["password"]
        user = db.session.query(User).filter(func.lower(User.email) == email).first()
        if not user or not user.check_password(password):
            abort(401, message="Invalid credentials")
        token = create_access_token(subject=user.email)
        return {"access_token": token}
