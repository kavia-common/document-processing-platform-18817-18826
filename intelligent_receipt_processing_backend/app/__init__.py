from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from .config import get_config
from .models import db
from .routes.health import blp as health_blp
from .routes.auth import blp as auth_blp
from .routes.documents import blp as documents_blp
from .routes.search import blp as search_blp
from .routes.jobs import blp as jobs_blp
from .routes.admin import blp as admin_blp


app = Flask(__name__)
app.url_map.strict_slashes = False

# Load config
app.config.from_object(get_config())

# CORS
CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

# OpenAPI metadata already set in Config
api = Api(app, spec_kwargs={"tags": [
    {"name": "Health", "description": "Health check route"},
    {"name": "Auth", "description": "Authentication endpoints"},
    {"name": "Documents", "description": "Document upload and management"},
    {"name": "Search", "description": "Search documents"},
    {"name": "Jobs", "description": "Processing jobs endpoints"},
    {"name": "Admin", "description": "Admin operations"},
]})

# Database
app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///local.db")  # fallback for dev
db.init_app(app)
with app.app_context():
    db.create_all()

# Register blueprints
api.register_blueprint(health_blp)
api.register_blueprint(auth_blp)
api.register_blueprint(documents_blp)
api.register_blueprint(search_blp)
api.register_blueprint(jobs_blp)
api.register_blueprint(admin_blp)
