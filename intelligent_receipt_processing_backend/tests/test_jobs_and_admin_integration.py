import io


def test_jobs_list_and_detail(client, auth_header):
    # Upload to create a job synchronously
    data = {
        "title": "Test OCR Job",
        "file": (io.BytesIO(b"OCR processed content test"), "ocr.txt"),
    }
    up = client.post("/documents", headers=auth_header, data=data, content_type="multipart/form-data")
    assert up.status_code == 201

    # List jobs for current user
    jobs = client.get("/jobs", headers=auth_header)
    assert jobs.status_code == 200
    job_list = jobs.get_json()
    assert isinstance(job_list, list) and len(job_list) >= 1
    job_id = job_list[0]["id"]

    # Get job detail
    job_detail = client.get(f"/jobs/{job_id}", headers=auth_header)
    assert job_detail.status_code == 200
    jd = job_detail.get_json()
    assert jd["id"] == job_id
    assert jd["status"] in ("PENDING", "RUNNING", "SUCCESS", "FAILED")


def test_admin_endpoints_require_admin(client, auth_header, ensure_admin):
    # Non-admin should get 403 for admin endpoints
    non_admin_jobs = client.get("/admin/jobs", headers=auth_header)
    assert non_admin_jobs.status_code == 403
    non_admin_docs = client.get("/admin/documents", headers=auth_header)
    assert non_admin_docs.status_code == 403

    # Login as admin to access admin endpoints
    admin_login = client.post("/auth/login", json={"email": ensure_admin["email"], "password": ensure_admin["password"]})
    assert admin_login.status_code == 200
    admin_token = admin_login.get_json()["access_token"]
    admin_auth = {"Authorization": f"Bearer {admin_token}"}

    # Admin can list jobs and documents
    aj = client.get("/admin/jobs", headers=admin_auth)
    assert aj.status_code == 200
    assert isinstance(aj.get_json(), list)

    ad = client.get("/admin/documents", headers=admin_auth)
    assert ad.status_code == 200
    assert isinstance(ad.get_json(), list)
