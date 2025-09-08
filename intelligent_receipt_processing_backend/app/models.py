from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = db.relationship("Document", secondary="user_documents", back_populates="users")

    def set_password(self, password: str, rounds: int = 12):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), nullable=False)
    filename = db.Column(db.String(1024), nullable=False)  # original filename
    mime_type = db.Column(db.String(255), nullable=True)
    extension = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(128), nullable=True, index=True)  # auto-categorized label
    tags = db.Column(db.Text, nullable=True)  # comma separated tags
    description = db.Column(db.Text, nullable=True)

    latest_version_id = db.Column(db.Integer, db.ForeignKey("document_versions.id"), nullable=True)

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_by = db.relationship("User", foreign_keys=[created_by_id])

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions = db.relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    users = db.relationship("User", secondary="user_documents", back_populates="documents")


class DocumentVersion(db.Model):
    __tablename__ = "document_versions"
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False, index=True)
    storage_path = db.Column(db.String(2048), nullable=False)  # path relative to STORAGE_ROOT
    checksum = db.Column(db.String(128), nullable=True, index=True)
    size_bytes = db.Column(db.Integer, nullable=True)
    ocr_text = db.Column(db.Text, nullable=True)
    ocr_json = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    document = db.relationship("Document", back_populates="versions")
    # Back reference from Document.latest_version
    parents = db.relationship("Document", primaryjoin="Document.latest_version_id==DocumentVersion.id", viewonly=True)


class ProcessingJob(db.Model):
    __tablename__ = "processing_jobs"
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False, index=True)
    version_id = db.Column(db.Integer, db.ForeignKey("document_versions.id"), nullable=True, index=True)

    status = db.Column(db.Enum(JobStatus), nullable=False, default=JobStatus.PENDING)
    task_type = db.Column(db.String(64), nullable=False, default="OCR")
    message = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)

    document = db.relationship("Document")
    version = db.relationship("DocumentVersion")


class UserDocument(db.Model):
    __tablename__ = "user_documents"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), primary_key=True)
    role = db.Column(db.String(32), nullable=False, default="owner")  # owner, viewer, editor
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def apply_basic_indexes():
    """
    Apply additional indexes if needed at runtime in SQLite/dev, for MySQL use migrations in real projects.
    """
    # Placeholder: with Alembic you'd manage migrations. Here we rely on SQLAlchemy create_all.


def seed_admin_if_missing(db_session, email: str, password: str):
    admin = db_session.query(User).filter(func.lower(User.email) == email.lower()).first()
    if not admin:
        admin = User(email=email, name="Admin", is_admin=True)
        admin.set_password(password)
        db_session.add(admin)
        db_session.commit()
