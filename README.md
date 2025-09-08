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

Production run (Gunicorn):
- From the intelligent_receipt_processing_backend directory:
  - Ensure env vars are set (see .env.example). Do NOT hardcode secrets in code.
  - Run Gunicorn binding to 0.0.0.0:3001 with 4 workers and a threaded worker class:
    PORT=3001 gunicorn -b 0.0.0.0:${PORT} -w 4 --threads 2 "app:app"
  - You can tune workers/threads based on CPU and workload.
  - Open http://localhost:3001/docs

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

Database configuration:
- For MySQL, set MYSQL_SQLALCHEMY_URL to: mysql+pymysql://USER:PASSWORD@HOST:PORT/DBNAME
- If MYSQL_SQLALCHEMY_URL is blank or unset, the app falls back to SQLite at instance/local.db for development.
- For CI/testing, set FLASK_ENV=test and optionally TEST_MYSQL_SQLALCHEMY_URL.

Quick API test flow:
1) Register user:
   curl -s -X POST http://localhost:3001/auth/register -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"secret","name":"User"}'
   -> returns {"access_token": "..."}
2) Login (if user exists):
   curl -s -X POST http://localhost:3001/auth/login -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"secret"}'
3) List documents:
   curl -s -H "Authorization: Bearer <token>" http://localhost:3001/documents
4) Upload document:
   curl -s -X POST -H "Authorization: Bearer <token>" -F "title=Test Doc" -F "file=@/path/to/file.pdf" http://localhost:3001/documents
5) Check jobs:
   curl -s -H "Authorization: Bearer <token>" http://localhost:3001/jobs

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
