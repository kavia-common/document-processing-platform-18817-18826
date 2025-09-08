import mimetypes
import os

from flask import request, g, send_file
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from werkzeug.datastructures import FileStorage

from ..models import db, Document, DocumentVersion, ProcessingJob, JobStatus
from ..schemas import DocumentUploadSchema, DocumentResponseSchema, DocumentVersionResponseSchema
from ..services.storage_service import StorageService
from ..services.job_service import JobService
from .auth import require_auth

blp = Blueprint("Documents", "documents", url_prefix="/documents", description="Document upload and management")


@blp.route("")
class DocumentListResource(MethodView):
    @blp.response(200, DocumentResponseSchema(many=True))
    @require_auth
    def get(self):
        """
        List documents owned by the current user.
        """
        docs = db.session.query(Document).filter(Document.created_by_id == g.current_user.id).order_by(Document.updated_at.desc()).all()
        return docs

    @blp.arguments(DocumentUploadSchema, location="form")
    @blp.response(201, DocumentResponseSchema)
    @require_auth
    def post(self, form):
        """
        Upload a new document with a file.
        Accepts multipart/form-data with 'file' and fields from DocumentUploadSchema.
        """
        file: FileStorage = request.files.get("file")
        if not file or file.filename == "":
            abort(400, message="No file provided")
        from ..utils import allowed_file
        if not allowed_file(file.filename):
            abort(400, message="File type not allowed")

        title = form["title"]
        description = form.get("description")
        tags = form.get("tags")

        # Create Document row
        ext = (file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else None)
        mime_type = mimetypes.guess_type(file.filename)[0]
        doc = Document(
            title=title,
            filename=file.filename,
            mime_type=mime_type,
            extension=ext,
            created_by_id=g.current_user.id,
            description=description,
            tags=tags,
        )
        db.session.add(doc)
        db.session.flush()  # get doc.id

        storage = StorageService()
        rel_path, size, checksum = storage.save_new_version(g.current_user.id, doc.id, file.filename, file.stream)
        version = DocumentVersion(
            document_id=doc.id,
            storage_path=rel_path,
            checksum=checksum,
            size_bytes=size,
        )
        db.session.add(version)
        db.session.flush()
        doc.latest_version_id = version.id
        db.session.commit()

        # Create OCR job
        job = ProcessingJob(document_id=doc.id, version_id=version.id, status=JobStatus.PENDING, task_type="OCR")
        db.session.add(job)
        db.session.commit()

        # Synchronously run job for this prototype
        JobService().run_job(job.id)

        return doc


@blp.route("/<int:doc_id>")
class DocumentDetailResource(MethodView):
    @blp.response(200, DocumentResponseSchema)
    @require_auth
    def get(self, doc_id: int):
        """
        Get document details.
        """
        doc = db.session.get(Document, doc_id)
        if not doc or doc.created_by_id != g.current_user.id:
            abort(404, message="Document not found")
        return doc

    @blp.response(204)
    @require_auth
    def delete(self, doc_id: int):
        """
        Delete a document and all versions.
        """
        doc = db.session.get(Document, doc_id)
        if not doc or doc.created_by_id != g.current_user.id:
            abort(404, message="Document not found")
        db.session.delete(doc)
        db.session.commit()
        return ""


@blp.route("/<int:doc_id>/download")
class DocumentDownloadResource(MethodView):
    @require_auth
    def get(self, doc_id: int):
        """
        Download latest version file.
        """
        doc = db.session.get(Document, doc_id)
        if not doc or doc.created_by_id != g.current_user.id:
            abort(404, message="Document not found")

        version = db.session.get(DocumentVersion, doc.latest_version_id) if doc.latest_version_id else None
        if not version:
            abort(404, message="Version not found")

        from ..services.storage_service import StorageService
        storage = StorageService()
        abs_path = storage.get_absolute_path(version.storage_path)
        if not os.path.exists(abs_path):
            abort(404, message="File missing on storage")

        return send_file(abs_path, as_attachment=True, download_name=doc.filename)


@blp.route("/<int:doc_id>/versions")
class DocumentVersionListResource(MethodView):
    @blp.response(200, DocumentVersionResponseSchema(many=True))
    @require_auth
    def get(self, doc_id: int):
        """
        List versions for a document.
        """
        doc = db.session.get(Document, doc_id)
        if not doc or doc.created_by_id != g.current_user.id:
            abort(404, message="Document not found")
        versions = db.session.query(DocumentVersion).filter(DocumentVersion.document_id == doc.id).order_by(DocumentVersion.created_at.desc()).all()
        return versions

    @require_auth
    @blp.response(201, DocumentResponseSchema)
    def post(self, doc_id: int):
        """
        Upload a new version for a document (multipart/form-data with 'file').
        """
        doc = db.session.get(Document, doc_id)
        if not doc or doc.created_by_id != g.current_user.id:
            abort(404, message="Document not found")

        file = request.files.get("file")
        if not file or file.filename == "":
            abort(400, message="No file provided")
        from ..utils import allowed_file
        if not allowed_file(file.filename):
            abort(400, message="File type not allowed")

        storage = StorageService()
        rel_path, size, checksum = storage.save_new_version(g.current_user.id, doc.id, file.filename, file.stream)
        version = DocumentVersion(
            document_id=doc.id,
            storage_path=rel_path,
            checksum=checksum,
            size_bytes=size,
        )
        db.session.add(version)
        db.session.flush()
        doc.latest_version_id = version.id
        db.session.commit()

        # enqueue OCR job
        job = ProcessingJob(document_id=doc.id, version_id=version.id, status=JobStatus.PENDING, task_type="OCR")
        db.session.add(job)
        db.session.commit()
        JobService().run_job(job.id)

        return doc
