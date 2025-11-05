"""Entity API endpoint tests."""

from fastapi.testclient import TestClient


def test_create_entity(client: TestClient) -> None:
    """Test entity creation.

    Args:
        client: Test client
    """
    # Create document and annotation
    document_data = {
        "title": "Test Document",
        "text": "Patient presents with fever and cough.",
    }
    doc_response = client.post("/api/v1/documents/", json=document_data)
    document_id = doc_response.json()["id"]

    annotation_data = {
        "document_id": document_id,
        "annotator_id": "test_annotator",
    }
    ann_response = client.post("/api/v1/annotations/", json=annotation_data)
    annotation_id = ann_response.json()["id"]

    # Create an entity
    entity_data = {
        "text": "fever",
        "entity_type": "symptom",
        "start_char": 22,
        "end_char": 27,
        "annotation_id": annotation_id,
        "confidence": 1.0,
    }

    response = client.post("/api/v1/entities/", json=entity_data)
    assert response.status_code == 200

    data = response.json()
    assert data["text"] == entity_data["text"]
    assert data["entity_type"] == entity_data["entity_type"]
    assert "id" in data


def test_create_entity_invalid_annotation(client: TestClient) -> None:
    """Test entity creation with invalid annotation ID.

    Args:
        client: Test client
    """
    entity_data = {
        "text": "fever",
        "entity_type": "symptom",
        "start_char": 0,
        "end_char": 5,
        "annotation_id": 9999,
        "confidence": 1.0,
    }

    response = client.post("/api/v1/entities/", json=entity_data)
    assert response.status_code == 404
    assert "annotation not found" in response.json()["detail"].lower()


def test_list_entities(client: TestClient) -> None:
    """Test listing entities.

    Args:
        client: Test client
    """
    # Setup: create document, annotation, and entity
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Patient with fever"}
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/", json={"document_id": doc_id, "annotator_id": "ann1"}
    )
    ann_id = ann_response.json()["id"]

    client.post(
        "/api/v1/entities/",
        json={
            "text": "fever",
            "entity_type": "symptom",
            "start_char": 12,
            "end_char": 17,
            "annotation_id": ann_id,
        },
    )

    response = client.get("/api/v1/entities/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_entities_filtered(client: TestClient) -> None:
    """Test listing entities filtered by annotation ID.

    Args:
        client: Test client
    """
    # Setup: create document and annotation
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Patient with fever"}
    )
    doc_id = doc_response.json()["id"]

    ann_response1 = client.post(
        "/api/v1/annotations/", json={"document_id": doc_id, "annotator_id": "ann1"}
    )
    ann_id1 = ann_response1.json()["id"]

    # Create entity in first annotation
    client.post(
        "/api/v1/entities/",
        json={
            "text": "fever",
            "entity_type": "symptom",
            "start_char": 12,
            "end_char": 17,
            "annotation_id": ann_id1,
        },
    )

    # List entities for first annotation only
    response = client.get(f"/api/v1/entities/?annotation_id={ann_id1}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["annotation_id"] == ann_id1


def test_get_entity(client: TestClient) -> None:
    """Test getting a specific entity.

    Args:
        client: Test client
    """
    # Setup
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Patient with fever"}
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/", json={"document_id": doc_id, "annotator_id": "ann1"}
    )
    ann_id = ann_response.json()["id"]

    entity_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "fever",
            "entity_type": "symptom",
            "start_char": 12,
            "end_char": 17,
            "annotation_id": ann_id,
        },
    )
    entity_id = entity_response.json()["id"]

    response = client.get(f"/api/v1/entities/{entity_id}")
    assert response.status_code == 200
    assert response.json()["id"] == entity_id


def test_get_entity_not_found(client: TestClient) -> None:
    """Test getting a non-existent entity.

    Args:
        client: Test client
    """
    response = client.get("/api/v1/entities/9999")
    assert response.status_code == 404


def test_update_entity(client: TestClient) -> None:
    """Test updating an entity.

    Args:
        client: Test client
    """
    # Setup
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Patient with fever"}
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/", json={"document_id": doc_id, "annotator_id": "ann1"}
    )
    ann_id = ann_response.json()["id"]

    entity_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "fever",
            "entity_type": "symptom",
            "start_char": 12,
            "end_char": 17,
            "annotation_id": ann_id,
            "confidence": 0.8,
        },
    )
    entity_id = entity_response.json()["id"]

    # Update entity
    update_data = {"confidence": 0.95}
    response = client.put(f"/api/v1/entities/{entity_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["confidence"] == 0.95


def test_delete_entity(client: TestClient) -> None:
    """Test deleting an entity.

    Args:
        client: Test client
    """
    # Setup
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Doc", "text": "Patient with fever"}
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/", json={"document_id": doc_id, "annotator_id": "ann1"}
    )
    ann_id = ann_response.json()["id"]

    entity_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "fever",
            "entity_type": "symptom",
            "start_char": 12,
            "end_char": 17,
            "annotation_id": ann_id,
        },
    )
    entity_id = entity_response.json()["id"]

    # Delete entity
    response = client.delete(f"/api/v1/entities/{entity_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"].lower()
