"""Database configuration and session management."""

import os
from collections.abc import Generator

from sqlalchemy import delete
from sqlmodel import Session, SQLModel, create_engine

from src.config import settings

# Global engine - will be initialized on first use
_engine = None


def get_engine():
    """Get or create the database engine.

    Returns the appropriate engine based on environment (test or production).

    Returns:
        SQLAlchemy engine
    """
    global _engine

    if _engine is not None:
        return _engine

    # Determine which database to use
    if os.getenv("PYTEST_CURRENT_TEST"):
        database_url = settings.test_db_url
    else:
        database_url = os.getenv("DATABASE_URL") or settings.database_url

    # Ensure the directory exists for SQLite databases
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    _engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=True,  # Set to False in production
    )

    return _engine


def create_db_and_tables() -> None:
    """Create database tables."""
    eng = get_engine()
    SQLModel.metadata.create_all(eng)


def wipe_database() -> None:
    """Delete all data from all tables while keeping the tables intact.

    This function truncates all tables, effectively wiping the database
    while preserving the schema.
    """
    eng = get_engine()
    with Session(eng) as session:
        # Get all table names from metadata in reverse order (for FK constraints)
        tables = list(reversed(SQLModel.metadata.sorted_tables))

        for table in tables:
            session.exec(delete(table))

        session.commit()


def get_session() -> Generator[Session]:
    """Get database session.

    Yields:
        Database session
    """
    eng = get_engine()
    with Session(eng) as session:
        yield session

