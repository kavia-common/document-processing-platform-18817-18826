# document-processing-platform-18817-18826

Intelligent Receipt/Document Processing Platform

Backend (Flask) container included:
- Authentication (register/login) with signed tokens
- Document upload, versioning, download
- OCR extraction (stub) and auto-categorization
- Search
- Job tracking and Admin endpoints
- OpenAPI docs at /docs
- MySQL via SQLAlchemy (use MYSQL_SQLALCHEMY_URL), with SQLite fallback for dev

Run locally:
1. python -m venv .venv && source .venv/bin/activate
2. pip install -r intelligent_receipt_processing_backend/requirements.txt
3. cp intelligent_receipt_processing_backend/.env.example intelligent_receipt_processing_backend/.env (optional if you set envs another way)
4. FLASK_ENV=development PORT=3001 python intelligent_receipt_processing_backend/run.py
5. Open http://localhost:3001/docs

Environment variables (see .env.example):
- APP_SECRET_KEY
- MYSQL_SQLALCHEMY_URL
- CORS_ORIGINS
- ACCESS_TOKEN_EXPIRES_HOURS
- REFRESH_TOKEN_EXPIRES_DAYS
- STORAGE_ROOT
- MAX_CONTENT_LENGTH_MB
- DB_POOL_SIZE
- DB_MAX_OVERFLOW

API overview:
- GET / -> Health
- POST /auth/register, POST /auth/login
- GET/POST /documents; GET/DELETE /documents/{id}; GET /documents/{id}/versions; GET /documents/{id}/download
- GET /search?q=...&category=...&tag=...
- GET /jobs; GET /jobs/{id}
- Admin: GET /admin/jobs; GET /admin/documents

Notes:
- OCR is a stub; replace OCRService with real provider integrations.
- For production, move the job execution to a background worker (Celery/RQ) and storage to a persistent volume or object storage.
