"""Document model for medical texts."""

import datetime
from datetime import datetime as dt
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel  # pyright: ignore[reportUnknownVariableType]

if TYPE_CHECKING:
    from src.models.annotation import Annotation


class Document(SQLModel, table=True):
    """Document model representing medical text to be annotated."""

    __tablename__ = "documents"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(default="", index=True)
    text: str = Field(index=False)

    # Metadata
    created_at: dt = Field(default_factory=lambda: dt.now(datetime.UTC))
    updated_at: dt = Field(default_factory=lambda: dt.now(datetime.UTC))

    # Relationships
    annotations: list["Annotation"] = Relationship(back_populates="document")

