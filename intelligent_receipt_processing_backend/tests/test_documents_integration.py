import io


def test_list_documents_requires_auth(client):
    # No Authorization header should return unauthorized
    resp = client.get("/documents")
    assert resp.status_code == 401


def test_upload_document_and_versions_flow(client, auth_header):
    # Initial list should be empty
    resp_list = client.get("/documents", headers=auth_header)
    assert resp_list.status_code == 200
    assert isinstance(resp_list.get_json(), list)
    initial_count = len(resp_list.get_json())

    # Upload a new document with multipart/form-data
    file_content = b"Store receipt total $19.99 change $0.01"
    data = {
        "title": "Grocery Receipt",
        "description": "Weekly groceries",
        "tags": "groceries,receipt",
        "file": (io.BytesIO(file_content), "receipt.txt"),
    }
    up = client.post("/documents", headers=auth_header, data=data, content_type="multipart/form-data")
    assert up.status_code == 201, up.data
    doc = up.get_json()
    assert doc["title"] == "Grocery Receipt"
    assert doc["filename"] == "receipt.txt"
    assert doc["latest_version_id"] is not None
    # Category should be assigned by stub categorizer
    assert doc["category"] in ("receipt", "uncategorized", "invoice", "tax", "legal")

    # List should now include the uploaded doc
    resp_list2 = client.get("/documents", headers=auth_header)
    assert resp_list2.status_code == 200
    assert len(resp_list2.get_json()) == initial_count + 1

    doc_id = doc["id"]

    # List versions
    versions = client.get(f"/documents/{doc_id}/versions", headers=auth_header)
    assert versions.status_code == 200
    versions_list = versions.get_json()
    assert isinstance(versions_list, list) and len(versions_list) >= 1

    # Add another version
    v2_data = {
        "file": (io.BytesIO(b"Updated receipt content total $29.99"), "receipt-v2.txt"),
    }
    add_v2 = client.post(f"/documents/{doc_id}/versions", headers=auth_header, data=v2_data, content_type="multipart/form-data")
    assert add_v2.status_code == 201
    updated_doc = add_v2.get_json()
    assert updated_doc["latest_version_id"] != doc["latest_version_id"]

    # Download latest file
    dl = client.get(f"/documents/{doc_id}/download", headers=auth_header)
    assert dl.status_code == 200
    assert dl.data is not None
    assert b"Updated receipt content" in dl.data or b"Store receipt total" in dl.data

    # Get document by id
    doc_detail = client.get(f"/documents/{doc_id}", headers=auth_header)
    assert doc_detail.status_code == 200
    assert doc_detail.get_json()["id"] == doc_id

    # Delete document
    delete_resp = client.delete(f"/documents/{doc_id}", headers=auth_header)
    assert delete_resp.status_code == 204

    # Fetch after delete should 404
    not_found = client.get(f"/documents/{doc_id}", headers=auth_header)
    assert not_found.status_code == 404
