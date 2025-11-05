"""Document API routes."""

import asyncio
import sys

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from src.agents import ExtractedEntitiesResponse, extract_medical_entities
from src.api.dependencies import SessionDep
from src.models import Document

# On Windows, set the event loop policy to WindowsSelectorEventLoopPolicy
# This fixes issues with asyncio and httpx on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=Document)
def create_document(document: Document, session: SessionDep) -> Document:
    """Create a new document.

    Args:
        document: Document data
        session: Database session

    Returns:
        Created document
    """
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.get("/", response_model=list[Document])
def list_documents(session: SessionDep, skip: int = 0, limit: int = 100) -> list[Document]:
    """List all documents.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of documents
    """
    statement = select(Document).offset(skip).limit(limit)
    documents = session.exec(statement).all()
    return list(documents)


@router.get("/{document_id}", response_model=Document)
def get_document(document_id: int, session: SessionDep) -> Document:
    """Get a specific document by ID.

    Args:
        document_id: Document ID
        session: Database session

    Returns:
        Document

    Raises:
        HTTPException: If document not found
    """
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.put("/{document_id}", response_model=Document)
def update_document(document_id: int, document_update: Document, session: SessionDep) -> Document:
    """Update a document.

    Args:
        document_id: Document ID
        document_update: Updated document data
        session: Database session

    Returns:
        Updated document

    Raises:
        HTTPException: If document not found
    """
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document_data = document_update.model_dump(exclude_unset=True)
    for key, value in document_data.items():
        setattr(document, key, value)

    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.delete("/{document_id}")
def delete_document(document_id: int, session: SessionDep) -> dict:
    """Delete a document.

    Args:
        document_id: Document ID
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If document not found
    """
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    session.delete(document)
    session.commit()
    return {"message": "Document deleted successfully"}


@router.post("/{document_id}/extract-entities", response_model=ExtractedEntitiesResponse)
async def extract_document_entities(document_id: int,
                                    session: SessionDep) -> ExtractedEntitiesResponse:
    """Extract medical entities from a document using PydanticAI.

    Args:
        document_id: Document ID
        session: Database session

    Returns:
        ExtractedEntitiesResponse with extracted entities

    Raises:
        HTTPException: If document not found or extraction fails
    """
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        response = await extract_medical_entities(document.text)

        # Fix character positions - LLMs are bad at counting characters
        # For each entity, find its actual position in the document text
        corrected_entities = []
        for entity in response.entities:
            # Find all occurrences of this entity text in the document
            search_text = entity.text
            start_pos = 0
            found = False

            while True:
                pos = document.text.find(search_text, start_pos)
                if pos == -1:
                    # Entity text not found - skip this entity
                    break

                # Found the text - use this position
                entity.start_char = pos
                entity.end_char = pos + len(search_text)
                corrected_entities.append(entity)
                found = True
                break

            if not found:
                # If exact text not found, try to find it case-insensitively
                search_text_lower = search_text.lower()
                pos = document.text.lower().find(search_text_lower)
                if pos != -1:
                    entity.start_char = pos
                    entity.end_char = pos + len(search_text)
                    # Update entity text to match actual casing in document
                    entity.text = document.text[pos:pos + len(search_text)]
                    corrected_entities.append(entity)

        response.entities = corrected_entities
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
