from datetime import datetime
from flask import current_app
from ..models import db, ProcessingJob, JobStatus, Document, DocumentVersion
from .ocr_service import OCRService
from .categorization_service import CategorizationService


class JobService:
    """
    Executes OCR and categorization jobs synchronously (simulate background).
    Integrate with Celery/RQ in production.
    """

    def __init__(self):
        self.ocr = OCRService()
        self.cat = CategorizationService()

    # PUBLIC_INTERFACE
    def run_job(self, job_id: int):
        """Run a job by id; updates DB with results."""
        job = db.session.get(ProcessingJob, job_id)
        if not job:
            return

        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        db.session.commit()

        try:
            version = db.session.get(DocumentVersion, job.version_id)
            if not version:
                raise ValueError("Version not found for job")

            text, ocr_json = self.ocr.extract_text(abs_path=current_app.config["STORAGE_ROOT"] + "/" + version.storage_path, mime_type=None)
            version.ocr_text = text
            version.ocr_json = ocr_json

            doc = db.session.get(Document, job.document_id)
            if doc:
                doc.category = self.cat.categorize(doc.title, text)

            job.status = JobStatus.SUCCESS
            job.finished_at = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            job.status = JobStatus.FAILED
            job.message = str(e)
            job.finished_at = datetime.utcnow()
            db.session.commit()
