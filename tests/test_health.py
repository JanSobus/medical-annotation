"""Health check and root endpoint tests."""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint returns welcome message.

    Args:
        client: Test client
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint.

    Args:
        client: Test client
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_wipe_db(client: TestClient) -> None:
    """Test wipe_db endpoint executes successfully.

    Args:
        client: Test client
    """
    # Wipe the database
    wipe_response = client.post("/wipe_db")
    assert wipe_response.status_code == 200
    data = wipe_response.json()
    assert "wiped successfully" in data["message"].lower()
    assert "empty" in data["message"].lower()


def test_dump_db_empty(client: TestClient) -> None:
    """Test database dump endpoint with empty database.

    Args:
        client: Test client
    """
    response = client.get("/dump_db")
    assert response.status_code == 200

    data = response.json()
    assert "documents" in data
    assert "annotations" in data
    assert "entities" in data
    assert "relations" in data
    assert isinstance(data["documents"], list)
    assert isinstance(data["annotations"], list)
    assert isinstance(data["entities"], list)
    assert isinstance(data["relations"], list)


def test_dump_db_with_data(client: TestClient) -> None:
    """Test database dump endpoint with data.

    Args:
        client: Test client
    """
    # Create test data
    doc_response = client.post(
        "/api/v1/documents/", json={"title": "Test Doc", "text": "Test text"}
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/",
        json={"document_id": doc_id, "annotator_id": "tester", "status": "in_progress"},
    )
    ann_id = ann_response.json()["id"]

    ent_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "test",
            "entity_type": "disease",
            "start_char": 0,
            "end_char": 4,
            "annotation_id": ann_id,
            "confidence": 1.0,
        },
    )
    ent_id = ent_response.json()["id"]

    ent2_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "medicine",
            "entity_type": "medication",
            "start_char": 5,
            "end_char": 13,
            "annotation_id": ann_id,
            "confidence": 1.0,
        },
    )
    ent2_id = ent2_response.json()["id"]

    client.post(
        "/api/v1/relations/",
        json={
            "annotation_id": ann_id,
            "source_entity_id": ent2_id,
            "target_entity_id": ent_id,
            "relation_type": "treats",
            "confidence": 0.9,
        },
    )

    # Dump database
    response = client.get("/dump_db")
    assert response.status_code == 200

    data = response.json()

    # Verify all tables have data
    assert len(data["documents"]) >= 1
    assert len(data["annotations"]) >= 1
    assert len(data["entities"]) >= 2
    assert len(data["relations"]) >= 1

    # Verify document data
    doc = data["documents"][0]
    assert doc["title"] == "Test Doc"
    assert doc["text"] == "Test text"
    assert "id" in doc
    assert "created_at" in doc
    assert "updated_at" in doc

    # Verify annotation data
    ann = data["annotations"][0]
    assert ann["document_id"] == doc_id
    assert ann["annotator_id"] == "tester"
    assert ann["status"] == "in_progress"

    # Verify entity data
    assert any(e["text"] == "test" for e in data["entities"])
    assert any(e["entity_type"] == "disease" for e in data["entities"])

    # Verify relation data
    assert any(r["relation_type"] == "treats" for r in data["relations"])
