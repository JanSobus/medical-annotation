"""Relation model for entity relationships."""

import datetime
from datetime import datetime as dt
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel  # pyright: ignore[reportUnknownVariableType]

if TYPE_CHECKING:
    from src.models.annotation import Annotation


class RelationType(StrEnum):
    """Types of relationships between entities."""

    TREATS = "treats"
    CAUSES = "causes"
    HAS_SYMPTOM = "has_symptom"
    INDICATES = "indicates"
    CONTRAINDICATES = "contraindicates"
    DOSAGE_FOR = "dosage_for"
    LOCATED_IN = "located_in"
    TEMPORAL = "temporal"
    OTHER = "other"


class Relation(SQLModel, table=True):
    """Relation model representing relationships between entities."""

    __tablename__ = "relations"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    relation_type: RelationType
    source_entity_id: int = Field(foreign_key="entities.id")
    target_entity_id: int = Field(foreign_key="entities.id")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    # Foreign keys
    annotation_id: int = Field(foreign_key="annotations.id")

    # Metadata
    created_at: dt = Field(default_factory=lambda: dt.now(datetime.UTC))
    updated_at: dt = Field(default_factory=lambda: dt.now(datetime.UTC))

    # Relationships
    annotation: "Annotation" = Relationship(back_populates="relations")

