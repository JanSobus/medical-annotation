"""Relation API endpoint tests."""

from fastapi.testclient import TestClient


def test_create_relation(client: TestClient) -> None:
    """Test relation creation.

    Args:
        client: Test client
    """
    # Setup: create document, annotation, and two entities
    doc_response = client.post(
        "/api/v1/documents/",
        json={"title": "Doc", "text": "Patient with fever and cough"},
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/", json={"document_id": doc_id, "annotator_id": "ann1"}
    )
    ann_id = ann_response.json()["id"]

    entity1_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "fever",
            "entity_type": "symptom",
            "start_char": 12,
            "end_char": 17,
            "annotation_id": ann_id,
        },
    )
    entity1_id = entity1_response.json()["id"]

    entity2_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "cough",
            "entity_type": "symptom",
            "start_char": 22,
            "end_char": 27,
            "annotation_id": ann_id,
        },
    )
    entity2_id = entity2_response.json()["id"]

    # Create a relation
    relation_data = {
        "annotation_id": ann_id,
        "source_entity_id": entity1_id,
        "target_entity_id": entity2_id,
        "relation_type": "indicates",
        "confidence": 0.95,
    }

    response = client.post("/api/v1/relations/", json=relation_data)
    assert response.status_code == 200

    data = response.json()
    assert data["source_entity_id"] == entity1_id
    assert data["target_entity_id"] == entity2_id
    assert data["relation_type"] == "indicates"
    assert "id" in data


def test_create_relation_invalid_annotation(client: TestClient) -> None:
    """Test relation creation with invalid annotation ID.

    Args:
        client: Test client
    """
    relation_data = {
        "annotation_id": 9999,
        "source_entity_id": 1,
        "target_entity_id": 2,
        "relation_type": "treats",
        "confidence": 0.95,
    }

    response = client.post("/api/v1/relations/", json=relation_data)
    assert response.status_code == 404
    assert "annotation not found" in response.json()["detail"].lower()


def test_list_relations(client: TestClient) -> None:
    """Test listing relations.

    Args:
        client: Test client
    """
    # Setup
    doc_response = client.post(
        "/api/v1/documents/",
        json={"title": "Doc", "text": "Patient with fever and cough"},
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/", json={"document_id": doc_id, "annotator_id": "ann1"}
    )
    ann_id = ann_response.json()["id"]

    entity1_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "fever",
            "entity_type": "symptom",
            "start_char": 12,
            "end_char": 17,
            "annotation_id": ann_id,
        },
    )
    entity1_id = entity1_response.json()["id"]

    entity2_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "cough",
            "entity_type": "symptom",
            "start_char": 22,
            "end_char": 27,
            "annotation_id": ann_id,
        },
    )
    entity2_id = entity2_response.json()["id"]

    client.post(
        "/api/v1/relations/",
        json={
            "annotation_id": ann_id,
            "source_entity_id": entity1_id,
            "target_entity_id": entity2_id,
            "relation_type": "indicates",
        },
    )

    response = client.get("/api/v1/relations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_relations_filtered(client: TestClient) -> None:
    """Test listing relations filtered by annotation ID.

    Args:
        client: Test client
    """
    # Setup with one annotation
    doc_response = client.post(
        "/api/v1/documents/",
        json={"title": "Doc", "text": "Patient with fever and cough"},
    )
    doc_id = doc_response.json()["id"]

    ann_response1 = client.post(
        "/api/v1/annotations/", json={"document_id": doc_id, "annotator_id": "ann1"}
    )
    ann_id1 = ann_response1.json()["id"]

    # Create entities in first annotation
    entity1_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "fever",
            "entity_type": "symptom",
            "start_char": 12,
            "end_char": 17,
            "annotation_id": ann_id1,
        },
    )
    entity1_id = entity1_response.json()["id"]

    entity2_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "cough",
            "entity_type": "symptom",
            "start_char": 22,
            "end_char": 27,
            "annotation_id": ann_id1,
        },
    )
    entity2_id = entity2_response.json()["id"]

    # Create relation in first annotation
    client.post(
        "/api/v1/relations/",
        json={
            "annotation_id": ann_id1,
            "source_entity_id": entity1_id,
            "target_entity_id": entity2_id,
            "relation_type": "indicates",
        },
    )

    # List relations for first annotation only
    response = client.get(f"/api/v1/relations/?annotation_id={ann_id1}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["annotation_id"] == ann_id1


def test_get_relation(client: TestClient) -> None:
    """Test getting a specific relation.

    Args:
        client: Test client
    """
    # Setup
    doc_response = client.post(
        "/api/v1/documents/",
        json={"title": "Doc", "text": "Patient with fever and cough"},
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/", json={"document_id": doc_id, "annotator_id": "ann1"}
    )
    ann_id = ann_response.json()["id"]

    entity1_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "fever",
            "entity_type": "symptom",
            "start_char": 12,
            "end_char": 17,
            "annotation_id": ann_id,
        },
    )
    entity1_id = entity1_response.json()["id"]

    entity2_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "cough",
            "entity_type": "symptom",
            "start_char": 22,
            "end_char": 27,
            "annotation_id": ann_id,
        },
    )
    entity2_id = entity2_response.json()["id"]

    relation_response = client.post(
        "/api/v1/relations/",
        json={
            "annotation_id": ann_id,
            "source_entity_id": entity1_id,
            "target_entity_id": entity2_id,
            "relation_type": "indicates",
        },
    )
    relation_id = relation_response.json()["id"]

    response = client.get(f"/api/v1/relations/{relation_id}")
    assert response.status_code == 200
    assert response.json()["id"] == relation_id


def test_get_relation_not_found(client: TestClient) -> None:
    """Test getting a non-existent relation.

    Args:
        client: Test client
    """
    response = client.get("/api/v1/relations/9999")
    assert response.status_code == 404


def test_update_relation(client: TestClient) -> None:
    """Test updating a relation.

    Args:
        client: Test client
    """
    # Setup
    doc_response = client.post(
        "/api/v1/documents/",
        json={"title": "Doc", "text": "Patient with fever and cough"},
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/", json={"document_id": doc_id, "annotator_id": "ann1"}
    )
    ann_id = ann_response.json()["id"]

    entity1_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "fever",
            "entity_type": "symptom",
            "start_char": 12,
            "end_char": 17,
            "annotation_id": ann_id,
        },
    )
    entity1_id = entity1_response.json()["id"]

    entity2_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "cough",
            "entity_type": "symptom",
            "start_char": 22,
            "end_char": 27,
            "annotation_id": ann_id,
        },
    )
    entity2_id = entity2_response.json()["id"]

    relation_response = client.post(
        "/api/v1/relations/",
        json={
            "annotation_id": ann_id,
            "source_entity_id": entity1_id,
            "target_entity_id": entity2_id,
            "relation_type": "indicates",
            "confidence": 0.85,
        },
    )
    relation_id = relation_response.json()["id"]

    # Update relation
    update_data = {"confidence": 0.95}
    response = client.put(f"/api/v1/relations/{relation_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["confidence"] == 0.95


def test_delete_relation(client: TestClient) -> None:
    """Test deleting a relation.

    Args:
        client: Test client
    """
    # Setup
    doc_response = client.post(
        "/api/v1/documents/",
        json={"title": "Doc", "text": "Patient with fever and cough"},
    )
    doc_id = doc_response.json()["id"]

    ann_response = client.post(
        "/api/v1/annotations/", json={"document_id": doc_id, "annotator_id": "ann1"}
    )
    ann_id = ann_response.json()["id"]

    entity1_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "fever",
            "entity_type": "symptom",
            "start_char": 12,
            "end_char": 17,
            "annotation_id": ann_id,
        },
    )
    entity1_id = entity1_response.json()["id"]

    entity2_response = client.post(
        "/api/v1/entities/",
        json={
            "text": "cough",
            "entity_type": "symptom",
            "start_char": 22,
            "end_char": 27,
            "annotation_id": ann_id,
        },
    )
    entity2_id = entity2_response.json()["id"]

    relation_response = client.post(
        "/api/v1/relations/",
        json={
            "annotation_id": ann_id,
            "source_entity_id": entity1_id,
            "target_entity_id": entity2_id,
            "relation_type": "indicates",
        },
    )
    relation_id = relation_response.json()["id"]

    # Delete relation
    response = client.delete(f"/api/v1/relations/{relation_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"].lower()
