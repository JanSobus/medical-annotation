"""Entity API routes."""
import datetime
from datetime import datetime as dt

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from src.api.dependencies import SessionDep
from src.models import Annotation, Entity

router = APIRouter(prefix="/entities", tags=["entities"])


@router.post("/", response_model=Entity)
def create_entity(entity: Entity, session: SessionDep) -> Entity:
    """Create a new entity.

    Args:
        entity: Entity data
        session: Database session

    Returns:
        Created entity

    Raises:
        HTTPException: If annotation not found
    """
    # Verify annotation exists
    annotation = session.get(Annotation, entity.annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    session.add(entity)
    session.commit()
    session.refresh(entity)

    # Update annotation's updated_at timestamp
    annotation.updated_at = dt.now(datetime.UTC)
    session.add(annotation)
    session.commit()

    # Refresh entity to ensure it has all updated values
    session.refresh(entity)
    return entity


@router.get("/", response_model=list[Entity])
def list_entities(
    session: SessionDep, annotation_id: int | None = None, skip: int = 0, limit: int = 100
) -> list[Entity]:
    """List entities, optionally filtered by annotation.

    Args:
        session: Database session
        annotation_id: Optional annotation ID filter
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of entities
    """
    statement = select(Entity)
    if annotation_id is not None:
        statement = statement.where(Entity.annotation_id == annotation_id)
    statement = statement.offset(skip).limit(limit)

    entities = session.exec(statement).all()
    return list(entities)


@router.get("/{entity_id}", response_model=Entity)
def get_entity(entity_id: int, session: SessionDep) -> Entity:
    """Get a specific entity by ID.

    Args:
        entity_id: Entity ID
        session: Database session

    Returns:
        Entity

    Raises:
        HTTPException: If entity not found
    """
    entity = session.get(Entity, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.put("/{entity_id}", response_model=Entity)
def update_entity(entity_id: int, entity_update: Entity, session: SessionDep) -> Entity:
    """Update an entity.

    Args:
        entity_id: Entity ID
        entity_update: Updated entity data
        session: Database session

    Returns:
        Updated entity

    Raises:
        HTTPException: If entity not found
    """


    entity = session.get(Entity, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Only update specific fields, skip id and annotation_id
    updatable_fields = {"text", "entity_type", "start_char", "end_char", "confidence"}
    entity_data = entity_update.model_dump(exclude_unset=True)
    for key, value in entity_data.items():
        if key in updatable_fields and value is not None:
            setattr(entity, key, value)

    # Update the updated_at timestamp
    entity.updated_at = dt.now(datetime.UTC)

    session.add(entity)
    session.commit()
    session.refresh(entity)

    # Update annotation's updated_at timestamp
    annotation = session.get(Annotation, entity.annotation_id)
    if annotation:
        annotation.updated_at = dt.now(datetime.UTC)
        session.add(annotation)
        session.commit()

    # Refresh entity to ensure it has all updated values
    session.refresh(entity)
    return entity


@router.delete("/{entity_id}")
def delete_entity(entity_id: int, session: SessionDep) -> dict:
    """Delete an entity.

    Args:
        entity_id: Entity ID
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If entity not found
    """
    entity = session.get(Entity, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    annotation_id = entity.annotation_id
    session.delete(entity)
    session.commit()

    # Update annotation's updated_at timestamp
    annotation = session.get(Annotation, annotation_id)
    if annotation:
        annotation.updated_at = dt.now(datetime.UTC)
        session.add(annotation)
        session.commit()

    return {"message": "Entity deleted successfully"}

