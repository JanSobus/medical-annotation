"""Entity model for medical text annotations."""

import datetime
from datetime import datetime as dt
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel  # pyright: ignore[reportUnknownVariableType]

if TYPE_CHECKING:
    from src.models.annotation import Annotation


class EntityType(StrEnum):
    """Medical entity types."""

    DISEASE = "disease"
    MEDICATION = "medication"
    SYMPTOM = "symptom"
    PROCEDURE = "procedure"
    ANATOMY = "anatomy"
    LAB_VALUE = "lab_value"
    DOSAGE = "dosage"
    OTHER = "other"


class Entity(SQLModel, table=True):
    """Entity model representing annotated medical entities."""

    __tablename__ = "entities"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    text: str = Field(index=True)
    entity_type: EntityType
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    # Foreign key
    annotation_id: int = Field(foreign_key="annotations.id")

    # Metadata
    created_at: dt = Field(default_factory=lambda: dt.now(datetime.UTC))
    updated_at: dt = Field(default_factory=lambda: dt.now(datetime.UTC))

    # Relationships
    annotation: "Annotation" = Relationship(back_populates="entities")

