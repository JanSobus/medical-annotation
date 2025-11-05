"""Annotation API endpoint tests."""

from fastapi.testclient import TestClient


def test_create_annotation(client: TestClient) -> None:
    """Test annotation creation.

    Args:
        client: Test client
    """
    # Create a document first
    document_data = {
        "title": "Test Document",
        "text": "Patient presents with fever and cough.",
    }
    doc_response = client.post("/api/v1/documents/", json=document_data)
    document_id = doc_response.json()["id"]

    # Create an annotation
    annotation_data = {
        "document_id": document_id,
        "annotator_id": "test_annotator",
        "status": "in_progress",
    }

    response = client.post("/api/v1/annotations/", json=annotation_data)
    assert response.status_code == 200

    data = response.json()
    assert data["document_id"] == document_id
    assert data["annotator_id"] == annotation_data["annotator_id"]
    assert "id" in data


def test_create_annotation_invalid_document(client: TestClient) -> None:
    """Test annotation creation with invalid document ID.

    Args:
        client: Test client
    """
    annotation_data = {
        "document_id": 9999,
        "annotator_id": "test_annotator",
        "status": "in_progress",
    }

    response = client.post("/api/v1/annotations/", json=annotation_data)
    assert response.status_code == 404
    assert "document not found" in response.json()["detail"].lower()


def test_list_annotations(client: TestClient) -> None:
    """Test listing annotations.

    Args:
        client: Test client
    """
    # Create document and annotation
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Text"}
    )
    doc_id = doc_response.json()["id"]

    client.post(
        "/api/v1/annotations/",
        json={"document_id": doc_id, "annotator_id": "ann1", "status": "completed"},
    )

    response = client.get("/api/v1/annotations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_annotation(client: TestClient) -> None:
    """Test getting a specific annotation.

    Args:
        client: Test client
    """
    # Create document and annotation
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Text"}
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/",
        json={"document_id": doc_id, "annotator_id": "ann1", "status": "completed"},
    )
    ann_id = ann_response.json()["id"]

    response = client.get(f"/api/v1/annotations/{ann_id}")
    assert response.status_code == 200
    assert response.json()["id"] == ann_id


def test_get_annotation_not_found(client: TestClient) -> None:
    """Test getting a non-existent annotation.

    Args:
        client: Test client
    """
    response = client.get("/api/v1/annotations/9999")
    assert response.status_code == 404


def test_update_annotation(client: TestClient) -> None:
    """Test updating an annotation.

    Args:
        client: Test client
    """
    # Create document and annotation
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Text"}
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/",
        json={"document_id": doc_id, "annotator_id": "ann1", "status": "in_progress"},
    )
    ann_id = ann_response.json()["id"]

    # Update annotation
    update_data = {"status": "completed"}
    response = client.put(f"/api/v1/annotations/{ann_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_delete_annotation(client: TestClient) -> None:
    """Test deleting an annotation.

    Args:
        client: Test client
    """
    # Create document and annotation
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Text"}
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/",
        json={"document_id": doc_id, "annotator_id": "ann1", "status": "in_progress"},
    )
    ann_id = ann_response.json()["id"]

    # Delete annotation
    response = client.delete(f"/api/v1/annotations/{ann_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"].lower()


def test_delete_annotation_not_found(client: TestClient) -> None:
    """Test deleting a non-existent annotation.

    Args:
        client: Test client
    """
    response = client.delete("/api/v1/annotations/9999")
    assert response.status_code == 404


def test_update_annotation_not_found(client: TestClient) -> None:
    """Test updating a non-existent annotation.

    Args:
        client: Test client
    """
    response = client.put("/api/v1/annotations/9999", json={"status": "completed"})
    assert response.status_code == 404


def test_list_annotations_filter_by_document_id(client: TestClient) -> None:
    """Test filtering annotations by document_id.

    Args:
        client: Test client
    """
    # Create two documents
    doc1_response = client.post(
        "/api/v1/documents/", json={"title": "Doc 1", "text": "Text 1"}
    )
    doc1_id = doc1_response.json()["id"]

    doc2_response = client.post(
        "/api/v1/documents/", json={"title": "Doc 2", "text": "Text 2"}
    )
    doc2_id = doc2_response.json()["id"]

    # Create annotations for both documents
    client.post(
        "/api/v1/annotations/",
        json={"document_id": doc1_id, "annotator_id": "ann1", "status": "in_progress"},
    )
    client.post(
        "/api/v1/annotations/",
        json={"document_id": doc2_id, "annotator_id": "ann1", "status": "completed"},
    )

    # Filter by document_id
    response = client.get(f"/api/v1/annotations/?document_id={doc1_id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["document_id"] == doc1_id


def test_list_annotations_filter_by_annotator_id(client: TestClient) -> None:
    """Test filtering annotations by annotator_id.

    Args:
        client: Test client
    """
    # Create a document
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Text"}
    )
    doc_id = doc_response.json()["id"]

    # Create annotations with different annotators
    client.post(
        "/api/v1/annotations/",
        json={"document_id": doc_id, "annotator_id": "alice", "status": "in_progress"},
    )
    client.post(
        "/api/v1/annotations/",
        json={"document_id": doc_id, "annotator_id": "bob", "status": "completed"},
    )

    # Filter by annotator_id
    response = client.get("/api/v1/annotations/?annotator_id=alice")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["annotator_id"] == "alice"


def test_list_annotations_filter_by_both(client: TestClient) -> None:
    """Test filtering annotations by both document_id and annotator_id.

    Args:
        client: Test client
    """
    # Create two documents
    doc1_response = client.post(
        "/api/v1/documents/", json={"title": "Doc 1", "text": "Text 1"}
    )
    doc1_id = doc1_response.json()["id"]

    doc2_response = client.post(
        "/api/v1/documents/", json={"title": "Doc 2", "text": "Text 2"}
    )
    doc2_id = doc2_response.json()["id"]

    # Create various annotations
    client.post(
        "/api/v1/annotations/",
        json={"document_id": doc1_id, "annotator_id": "alice", "status": "in_progress"},
    )
    client.post(
        "/api/v1/annotations/",
        json={"document_id": doc1_id, "annotator_id": "bob", "status": "completed"},
    )
    client.post(
        "/api/v1/annotations/",
        json={"document_id": doc2_id, "annotator_id": "alice", "status": "not_started"},
    )

    # Filter by both document_id and annotator_id
    response = client.get(f"/api/v1/annotations/?document_id={doc1_id}&annotator_id=alice")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["document_id"] == doc1_id
    assert data[0]["annotator_id"] == "alice"


def test_list_annotations_with_pagination(client: TestClient) -> None:
    """Test listing annotations with skip and limit.

    Args:
        client: Test client
    """
    # Create a document
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Text"}
    )
    doc_id = doc_response.json()["id"]

    # Create multiple annotations
    for i in range(3):
        client.post(
            "/api/v1/annotations/",
            json={
                "document_id": doc_id,
                "annotator_id": f"ann{i}",
                "status": "in_progress",
            },
        )

    # Test skip and limit
    response = client.get("/api/v1/annotations/?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_annotation_timestamps(client: TestClient) -> None:
    """Test that created_at and updated_at timestamps are set correctly.

    Args:
        client: Test client
    """
    # Create a document
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Text"}
    )
    doc_id = doc_response.json()["id"]

    # Create an annotation
    ann_response = client.post(
        "/api/v1/annotations/",
        json={"document_id": doc_id, "annotator_id": "ann1", "status": "in_progress"},
    )
    assert ann_response.status_code == 200

    data = ann_response.json()
    assert "created_at" in data
    assert "updated_at" in data
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_update_annotation_updates_timestamp(client: TestClient) -> None:
    """Test that updating an annotation updates the updated_at timestamp.

    Args:
        client: Test client
    """
    # Create document and annotation
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Text"}
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/",
        json={"document_id": doc_id, "annotator_id": "ann1", "status": "in_progress"},
    )
    ann_id = ann_response.json()["id"]
    original_updated_at = ann_response.json()["updated_at"]

    # Small delay to ensure timestamp difference
    import time

    time.sleep(0.1)

    # Update annotation
    update_response = client.put(
        f"/api/v1/annotations/{ann_id}", json={"status": "completed"}
    )
    assert update_response.status_code == 200

    updated_data = update_response.json()
    assert updated_data["updated_at"] != original_updated_at


def test_create_annotation_with_default_status(client: TestClient) -> None:
    """Test creating an annotation with default status.

    Args:
        client: Test client
    """
    # Create a document
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Text"}
    )
    doc_id = doc_response.json()["id"]

    # Create an annotation without specifying status
    annotation_data = {
        "document_id": doc_id,
        "annotator_id": "test_annotator",
    }

    response = client.post("/api/v1/annotations/", json=annotation_data)
    assert response.status_code == 200

    data = response.json()
    # Check that a status was assigned (default should be "not_started")
    assert "status" in data
