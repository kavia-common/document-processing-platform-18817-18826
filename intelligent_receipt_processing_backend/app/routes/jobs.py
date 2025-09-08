from flask import g
from flask.views import MethodView
from flask_smorest import Blueprint
from ..models import db, ProcessingJob
from ..schemas import JobResponseSchema
from .auth import require_auth

blp = Blueprint("Jobs", "jobs", url_prefix="/jobs", description="Processing jobs endpoints")


@blp.route("")
class JobsListResource(MethodView):
    @blp.response(200, JobResponseSchema(many=True))
    @require_auth
    def get(self):
        """
        List processing jobs for current user's documents.
        """
        q = db.session.query(ProcessingJob).join(ProcessingJob.document)
        q = q.filter(ProcessingJob.document.has(created_by_id=g.current_user.id))
        q = q.order_by(ProcessingJob.created_at.desc())
        return q.all()


@blp.route("/<int:job_id>")
class JobDetailResource(MethodView):
    @blp.response(200, JobResponseSchema)
    @require_auth
    def get(self, job_id: int):
        """
        Get job details.
        """
        job = db.session.get(ProcessingJob, job_id)
        if not job or job.document.created_by_id != g.current_user.id:
            from flask_smorest import abort
            abort(404, message="Job not found")
        return job
