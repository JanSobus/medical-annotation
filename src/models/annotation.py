"""Annotation model linking documents with entities and relations."""

import datetime
from datetime import datetime as dt
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel  # pyright: ignore[reportUnknownVariableType]

if TYPE_CHECKING:
    from src.models.document import Document
    from src.models.entity import Entity
    from src.models.relation import Relation


class AnnotationStatus(StrEnum):
    """Enum for annotation status values."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NOT_STARTED = "not_started"



class Annotation(SQLModel, table=True):
    """Annotation model representing a set of annotations for a document."""

    __tablename__ = "annotations"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    annotator_id: str = Field(default="", index=True)
    status: AnnotationStatus = Field(default=AnnotationStatus.NOT_STARTED)

    # Foreign key
    document_id: int = Field(foreign_key="documents.id")

    # Metadata
    created_at: dt = Field(default_factory=lambda: dt.now(datetime.UTC))
    updated_at: dt = Field(default_factory=lambda: dt.now(datetime.UTC))

    # Relationships
    document: "Document" = Relationship(back_populates="annotations")
    entities: list["Entity"] = Relationship(back_populates="annotation")
    relations: list["Relation"] = Relationship(back_populates="annotation")

