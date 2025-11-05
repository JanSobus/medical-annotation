"""Relation API routes."""

import datetime
from datetime import datetime as dt

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from src.api.dependencies import SessionDep
from src.models import Annotation, Relation

router = APIRouter(prefix="/relations", tags=["relations"])


@router.post("/", response_model=Relation)
def create_relation(relation: Relation, session: SessionDep) -> Relation:
    """Create a new relation.

    Args:
        relation: Relation data
        session: Database session

    Returns:
        Created relation

    Raises:
        HTTPException: If annotation not found
    """
    # Verify annotation exists
    annotation = session.get(Annotation, relation.annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    session.add(relation)
    session.commit()
    session.refresh(relation)

    # Update annotation's updated_at timestamp
    annotation.updated_at = dt.now(datetime.UTC)
    session.add(annotation)
    session.commit()

    # Refresh relation to ensure it has all updated values
    session.refresh(relation)
    return relation


@router.get("/", response_model=list[Relation])
def list_relations(
    session: SessionDep, annotation_id: int | None = None, skip: int = 0, limit: int = 100
) -> list[Relation]:
    """List relations, optionally filtered by annotation.

    Args:
        session: Database session
        annotation_id: Optional annotation ID filter
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of relations
    """
    statement = select(Relation)
    if annotation_id is not None:
        statement = statement.where(Relation.annotation_id == annotation_id)
    statement = statement.offset(skip).limit(limit)

    relations = session.exec(statement).all()
    return list(relations)


@router.get("/{relation_id}", response_model=Relation)
def get_relation(relation_id: int, session: SessionDep) -> Relation:
    """Get a specific relation by ID.

    Args:
        relation_id: Relation ID
        session: Database session

    Returns:
        Relation

    Raises:
        HTTPException: If relation not found
    """
    relation = session.get(Relation, relation_id)
    if not relation:
        raise HTTPException(status_code=404, detail="Relation not found")
    return relation


@router.put("/{relation_id}", response_model=Relation)
def update_relation(relation_id: int, relation_update: Relation, session: SessionDep) -> Relation:
    """Update a relation.

    Args:
        relation_id: Relation ID
        relation_update: Updated relation data
        session: Database session

    Returns:
        Updated relation

    Raises:
        HTTPException: If relation not found
    """
    relation = session.get(Relation, relation_id)
    if not relation:
        raise HTTPException(status_code=404, detail="Relation not found")

    # Only update specific fields, skip id and annotation_id
    updatable_fields = {"relation_type", "source_entity_id", "target_entity_id", "confidence"}
    relation_data = relation_update.model_dump(exclude_unset=True)
    for key, value in relation_data.items():
        if key in updatable_fields and value is not None:
            setattr(relation, key, value)

    # Update the updated_at timestamp
    relation.updated_at = dt.now(datetime.UTC)

    session.add(relation)
    session.commit()
    session.refresh(relation)

    # Update annotation's updated_at timestamp
    annotation = session.get(Annotation, relation.annotation_id)
    if annotation:
        annotation.updated_at = dt.now(datetime.UTC)
        session.add(annotation)
        session.commit()

    # Refresh relation to ensure it has all updated values
    session.refresh(relation)
    return relation


@router.delete("/{relation_id}")
def delete_relation(relation_id: int, session: SessionDep) -> dict:
    """Delete a relation.

    Args:
        relation_id: Relation ID
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If relation not found
    """
    relation = session.get(Relation, relation_id)
    if not relation:
        raise HTTPException(status_code=404, detail="Relation not found")

    annotation_id = relation.annotation_id
    session.delete(relation)
    session.commit()

    # Update annotation's updated_at timestamp
    annotation = session.get(Annotation, annotation_id)
    if annotation:
        annotation.updated_at = dt.now(datetime.UTC)
        session.add(annotation)
        session.commit()

    return {"message": "Relation deleted successfully"}

