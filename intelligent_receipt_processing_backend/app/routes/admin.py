from flask import g
from flask_smorest import Blueprint, abort
from ..models import db, ProcessingJob, Document
from ..schemas import JobResponseSchema, DocumentResponseSchema
from .auth import require_auth

blp = Blueprint("Admin", "admin", url_prefix="/admin", description="Admin operations")


def require_admin():
    if not getattr(g, "current_user", None) or not g.current_user.is_admin:
        abort(403, message="Admin privileges required")


@blp.route("/jobs")
class AdminJobsResource:
    @blp.response(200, JobResponseSchema(many=True))
    @require_auth
    def get(self):
        """
        List all processing jobs (admin only).
        """
        require_admin()
        q = db.session.query(ProcessingJob).order_by(ProcessingJob.created_at.desc())
        return q.all()


@blp.route("/documents")
class AdminDocumentsResource:
    @blp.response(200, DocumentResponseSchema(many=True))
    @require_auth
    def get(self):
        """
        List all documents (admin only).
        """
        require_admin()
        q = db.session.query(Document).order_by(Document.created_at.desc())
        return q.all()
