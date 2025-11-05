"""Annotation API routes."""

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from src.agents import (
    EntityReference,
    ExtractedRelationsResponse,
    extract_medical_relations,
)
from src.api.dependencies import SessionDep
from src.models import Annotation, Document, Entity

router = APIRouter(prefix="/annotations", tags=["annotations"])


@router.post("/", response_model=Annotation)
def create_annotation(annotation: Annotation, session: SessionDep) -> Annotation:
    """Create a new annotation.

    Args:
        annotation: Annotation data
        session: Database session

    Returns:
        Created annotation

    Raises:
        HTTPException: If document not found
    """
    # Verify document exists
    document = session.get(Document, annotation.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    session.add(annotation)
    session.commit()
    session.refresh(annotation)
    return annotation


@router.get("/", response_model=list[Annotation])
def list_annotations(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    document_id: int | None = None,
    annotator_id: str | None = None,
) -> list[Annotation]:
    """List all annotations with optional filtering.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        document_id: Optional filter by document ID
        annotator_id: Optional filter by annotator ID

    Returns:
        List of annotations
    """
    statement = select(Annotation)

    if document_id is not None:
        statement = statement.where(Annotation.document_id == document_id)

    if annotator_id is not None:
        statement = statement.where(Annotation.annotator_id == annotator_id)

    statement = statement.offset(skip).limit(limit)
    annotations = session.exec(statement).all()
    return list(annotations)


@router.get("/{annotation_id}", response_model=Annotation)
def get_annotation(annotation_id: int, session: SessionDep) -> Annotation:
    """Get a specific annotation by ID.

    Args:
        annotation_id: Annotation ID
        session: Database session

    Returns:
        Annotation with entities and relations

    Raises:
        HTTPException: If annotation not found
    """
    annotation = session.get(Annotation, annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation


@router.put("/{annotation_id}", response_model=Annotation)
def update_annotation(
    annotation_id: int, annotation_update: Annotation, session: SessionDep
) -> Annotation:
    """Update an annotation.

    Args:
        annotation_id: Annotation ID
        annotation_update: Updated annotation data
        session: Database session

    Returns:
        Updated annotation

    Raises:
        HTTPException: If annotation not found
    """
    import datetime
    from datetime import datetime as dt

    annotation = session.get(Annotation, annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    annotation_data = annotation_update.model_dump(exclude_unset=True)
    for key, value in annotation_data.items():
        setattr(annotation, key, value)

    # Update the updated_at timestamp
    annotation.updated_at = dt.now(datetime.UTC)

    session.add(annotation)
    session.commit()
    session.refresh(annotation)
    return annotation


@router.delete("/{annotation_id}")
def delete_annotation(annotation_id: int, session: SessionDep) -> dict:
    """Delete an annotation.

    Args:
        annotation_id: Annotation ID
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If annotation not found
    """
    annotation = session.get(Annotation, annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    session.delete(annotation)
    session.commit()
    return {"message": "Annotation deleted successfully"}


@router.post(
    "/{annotation_id}/extract-relations", response_model=ExtractedRelationsResponse
)
async def extract_annotation_relations(
    annotation_id: int, session: SessionDep
) -> ExtractedRelationsResponse:
    """Extract medical relationships from entities in an annotation using PydanticAI.

    Args:
        annotation_id: Annotation ID
        session: Database session

    Returns:
        ExtractedRelationsResponse with extracted relationships

    Raises:
        HTTPException: If annotation not found or has no entities
    """
    # Get the annotation
    annotation = session.get(Annotation, annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    # Get the document
    document = session.get(Document, annotation.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get all entities for this annotation
    entities = session.exec(
        select(Entity).where(Entity.annotation_id == annotation_id)
    ).all()

    if not entities:
        raise HTTPException(
            status_code=400, detail="No entities found for this annotation"
        )

    try:
        # Convert entities to EntityReference format for the agent
        entity_refs = [
            EntityReference(id=e.id, text=e.text, entity_type=e.entity_type)  # pyright: ignore[reportArgumentType]
            for e in entities
        ]

        # Extract relations using the AI agent
        response = await extract_medical_relations(document.text, entity_refs)

        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

