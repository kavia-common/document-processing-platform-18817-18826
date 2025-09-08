import io


def test_search_documents(client, auth_header):
    # Upload a document with title and content that imply "invoice"
    data = {
        "title": "ACME Invoice 2023-10",
        "description": "Billed services",
        "tags": "acme,finance",
        "file": (io.BytesIO(b"Amount due: $100.00 for services rendered"), "invoice.txt"),
    }
    up = client.post("/documents", headers=auth_header, data=data, content_type="multipart/form-data")
    assert up.status_code == 201
    doc = up.get_json()
    doc_id = doc["id"]

    # General search by q
    s1 = client.get("/search?q=invoice", headers=auth_header)
    assert s1.status_code == 200
    results = s1.get_json()
    assert any(d["id"] == doc_id for d in results)

    # Search by category (the stub categorizer should label as 'invoice')
    s2 = client.get("/search?category=invoice", headers=auth_header)
    assert s2.status_code == 200
    results2 = s2.get_json()
    assert any(d["id"] == doc_id for d in results2)

    # Search by tag substring
    s3 = client.get("/search?tag=acme", headers=auth_header)
    assert s3.status_code == 200
    results3 = s3.get_json()
    assert any(d["id"] == doc_id for d in results3)

    # Pagination params (limit/offset)
    s4 = client.get("/search?q=invoice&limit=1&offset=0", headers=auth_header)
    assert s4.status_code == 200
    assert isinstance(s4.get_json(), list)
