"""FastAPI application entry point."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import annotations, documents, entities, relations
from src.config import settings
from src.database import create_db_and_tables, get_session, wipe_database

# Load environment variables from .env file
# This ensures OPENAI_API_KEY and other env vars are available to all modules
load_dotenv()

# Ensure OPENAI_API_KEY is set for PydanticAI
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY not found in environment variables!")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan manager.

    Args:
        app: FastAPI application

    Yields:
        None
    """
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (cleanup if needed)


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/v1")
app.include_router(annotations.router, prefix="/api/v1")
app.include_router(entities.router, prefix="/api/v1")
app.include_router(relations.router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}


@app.post("/wipe_db")
def wipe_db() -> dict[str, str]:
    """Wipe all data from the database while keeping tables intact.

    WARNING: This endpoint deletes all data from all tables.
    Use with caution!

    Returns:
        Confirmation message
    """
    wipe_database()
    return {"message": "Database wiped successfully. All tables are now empty."}


@app.get("/dump_db")
def dump_db() -> dict[str, list[dict]]:
    """Dump all database contents into a single JSON response.

    Returns a dictionary containing all tables' data:
    - documents: List of all documents
    - annotations: List of all annotations
    - entities: List of all entities
    - relations: List of all relations

    Returns:
        Dictionary with all database contents
    """
    from sqlmodel import select

    from src.models import Annotation, Document, Entity, Relation

    session = next(get_session())

    try:
        # Fetch all data from each table
        documents = session.exec(select(Document)).all()
        annotations = session.exec(select(Annotation)).all()
        entities = session.exec(select(Entity)).all()
        relations = session.exec(select(Relation)).all()

        # Convert to dictionaries
        return {
            "documents": [doc.model_dump() for doc in documents],
            "annotations": [ann.model_dump() for ann in annotations],
            "entities": [ent.model_dump() for ent in entities],
            "relations": [rel.model_dump() for rel in relations],
        }
    finally:
        session.close()

