"""Document API endpoint tests."""

from fastapi.testclient import TestClient


def test_create_document(client: TestClient) -> None:
    """Test document creation.

    Args:
        client: Test client
    """
    document_data = {
        "title": "Test Document",
        "text": "Patient presents with fever and cough.",
    }

    response = client.post("/api/v1/documents/", json=document_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == document_data["title"]
    assert data["text"] == document_data["text"]
    assert "id" in data
    assert "created_at" in data


def test_list_documents(client: TestClient) -> None:
    """Test listing documents.

    Args:
        client: Test client
    """
    # Create a document first
    document_data = {
        "title": "Test Document",
        "text": "Patient presents with fever and cough.",
    }
    client.post("/api/v1/documents/", json=document_data)

    # List documents
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_documents_with_pagination(client: TestClient) -> None:
    """Test listing documents with skip and limit.

    Args:
        client: Test client
    """
    # Create multiple documents
    for i in range(3):
        client.post(
            "/api/v1/documents/",
            json={"title": f"Doc {i}", "text": f"Text {i}"},
        )

    # Test skip and limit
    response = client.get("/api/v1/documents/?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_get_document(client: TestClient) -> None:
    """Test getting a specific document.

    Args:
        client: Test client
    """
    # Create a document
    document_data = {
        "title": "Test Document",
        "text": "Patient presents with fever and cough.",
    }
    create_response = client.post("/api/v1/documents/", json=document_data)
    document_id = create_response.json()["id"]

    # Get the document
    response = client.get(f"/api/v1/documents/{document_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == document_id
    assert data["title"] == document_data["title"]


def test_get_document_not_found(client: TestClient) -> None:
    """Test getting a non-existent document.

    Args:
        client: Test client
    """
    response = client.get("/api/v1/documents/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_document(client: TestClient) -> None:
    """Test updating a document.

    Args:
        client: Test client
    """
    # Create a document
    create_response = client.post(
        "/api/v1/documents/", json={"title": "Original", "text": "Original text"}
    )
    doc_id = create_response.json()["id"]

    # Update the document
    update_data = {"title": "Updated Title"}
    response = client.put(f"/api/v1/documents/{doc_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == doc_id
    assert data["title"] == "Updated Title"


def test_update_document_not_found(client: TestClient) -> None:
    """Test updating a non-existent document.

    Args:
        client: Test client
    """
    response = client.put("/api/v1/documents/9999", json={"title": "New"})
    assert response.status_code == 404


def test_delete_document(client: TestClient) -> None:
    """Test deleting a document.

    Args:
        client: Test client
    """
    # Create a document
    create_response = client.post(
        "/api/v1/documents/", json={"title": "Delete me", "text": "Text"}
    )
    doc_id = create_response.json()["id"]

    # Delete the document
    response = client.delete(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"].lower()

    # Verify it's deleted
    get_response = client.get(f"/api/v1/documents/{doc_id}")
    assert get_response.status_code == 404


def test_delete_document_not_found(client: TestClient) -> None:
    """Test deleting a non-existent document.

    Args:
        client: Test client
    """
    response = client.delete("/api/v1/documents/9999")
    assert response.status_code == 404


def test_update_document_partial(client: TestClient) -> None:
    """Test partial update of a document (only text).

    Args:
        client: Test client
    """
    # Create a document
    create_response = client.post(
        "/api/v1/documents/",
        json={"title": "Original Title", "text": "Original text"},
    )
    doc_id = create_response.json()["id"]
    original_title = create_response.json()["title"]

    # Update only the text
    update_data = {"text": "Updated text content"}
    response = client.put(f"/api/v1/documents/{doc_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == doc_id
    assert data["title"] == original_title  # Title should remain unchanged
    assert data["text"] == "Updated text content"


def test_create_document_with_empty_text(client: TestClient) -> None:
    """Test creating a document with empty text.

    Args:
        client: Test client
    """
    document_data = {
        "title": "Empty Document",
        "text": "",
    }

    response = client.post("/api/v1/documents/", json=document_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == document_data["title"]
    assert data["text"] == ""


def test_create_document_with_long_text(client: TestClient) -> None:
    """Test creating a document with long text content.

    Args:
        client: Test client
    """
    long_text = "A" * 10000  # 10k characters
    document_data = {
        "title": "Long Document",
        "text": long_text,
    }

    response = client.post("/api/v1/documents/", json=document_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == document_data["title"]
    assert len(data["text"]) == 10000


def test_list_documents_empty(client: TestClient) -> None:
    """Test listing documents when database is empty.

    Args:
        client: Test client
    """
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


def test_document_timestamps(client: TestClient) -> None:
    """Test that created_at and updated_at timestamps are set correctly.

    Args:
        client: Test client
    """
    # Create a document
    document_data = {
        "title": "Timestamp Test",
        "text": "Testing timestamps",
    }

    response = client.post("/api/v1/documents/", json=document_data)
    assert response.status_code == 200

    data = response.json()
    assert "created_at" in data
    assert "updated_at" in data
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_update_document_full(client: TestClient) -> None:
    """Test full update of a document (both title and text).

    Args:
        client: Test client
    """
    # Create a document
    create_response = client.post(
        "/api/v1/documents/",
        json={"title": "Original Title", "text": "Original text"},
    )
    doc_id = create_response.json()["id"]

    # Update both title and text
    update_data = {"title": "New Title", "text": "New text content"}
    response = client.put(f"/api/v1/documents/{doc_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == doc_id
    assert data["title"] == "New Title"
    assert data["text"] == "New text content"


def test_list_documents_with_large_limit(client: TestClient) -> None:
    """Test listing documents with a large limit parameter.

    Args:
        client: Test client
    """
    # Create a few documents
    for i in range(3):
        client.post(
            "/api/v1/documents/",
            json={"title": f"Doc {i}", "text": f"Text {i}"},
        )

    # Get all with a large limit
    response = client.get("/api/v1/documents/?limit=1000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
