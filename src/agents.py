"""PydanticAI agents for medical text processing."""

import logging

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from src.models.entity import EntityType
from src.models.relation import RelationType

logger = logging.getLogger(__name__)


class ExtractedEntity(BaseModel):
    """Represents an extracted medical entity from text."""

    text: str = Field(
        ..., description="The exact text of the entity as it appears in the document"
    )
    entity_type: EntityType = Field(
        ...,
        description="The type of medical entity (disease, medication, symptom, etc.)",
    )
    start_char: int = Field(
        ...,
        description="Starting character position of the entity in the original text",
        ge=0,
    )
    end_char: int = Field(
        ...,
        description="Ending character position of the entity in the original text",
        ge=0,
    )
    confidence: float = Field(
        default=1.0,
        description="Confidence score for this extraction (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )


class ExtractedEntitiesResponse(BaseModel):
    """Response containing a list of extracted medical entities."""

    entities: list[ExtractedEntity] = Field(
        default_factory=list, description="List of extracted medical entities"
    )
    text: str = Field(
        ..., description="The original medical text that was analyzed"
    )


# System prompt for medical entity extraction
MEDICAL_ENTITY_SYSTEM_PROMPT = """You are an expert medical text annotation system. Your task \
is to extract medical entities from provided text.

Extract the following types of medical entities:
- DISEASE: Medical conditions, diagnoses, pathologies (e.g., "diabetes", "pneumonia", \
"hypertension")
- MEDICATION: Drug names, treatments, medications (e.g., "aspirin", "metformin", \
"chemotherapy")
- SYMPTOM: Clinical symptoms, signs, complaints (e.g., "fever", "chest pain", \
"shortness of breath")
- PROCEDURE: Medical procedures, tests, surgical interventions (e.g., "MRI", "biopsy", \
"bypass surgery")
- ANATOMY: Anatomical structures, body parts, organs (e.g., "heart", "liver", \
"left ventricle")
- LAB_VALUE: Laboratory test results, measurements (e.g., "HbA1c 7.5%", \
"blood glucose 120 mg/dL")
- DOSAGE: Drug dosages, measurements of medication (e.g., "500mg", "twice daily", \
"50 units")
- OTHER: Any other medically relevant entities that don't fit above categories

For each entity:
1. Extract the exact text as it appears in the document
2. Determine its character positions (start_char, end_char) in the original text
3. Classify it into one of the categories above
4. Assign a confidence score (1.0 = high confidence, lower for ambiguous cases)

Return all entities in the specified JSON format. Ensure accuracy and completeness in \
extraction. Be consistent with entity boundaries - do not include extra words or miss \
parts of entities."""


def create_medical_entity_agent() -> Agent[None, ExtractedEntitiesResponse]:
    """
    Create the medical entity extraction agent.

    Returns:
        Agent configured for extracting medical entities from text
    """
    logger.debug("Creating medical entity extraction agent...")
    agent = Agent(  # type: ignore[misc]
        model="openai:gpt-4o-mini",
        system_prompt=MEDICAL_ENTITY_SYSTEM_PROMPT,
        output_type=ExtractedEntitiesResponse,
        retries=2,
    )
    logger.debug("Agent created successfully")
    return agent


# Create a singleton instance
_medical_entity_agent: Agent[None, ExtractedEntitiesResponse] | None = None


def get_medical_entity_agent() -> Agent[None, ExtractedEntitiesResponse]:
    """Get or create the medical entity extraction agent."""
    global _medical_entity_agent
    if _medical_entity_agent is None:
        _medical_entity_agent = create_medical_entity_agent()
    return _medical_entity_agent


async def extract_medical_entities(text: str) -> ExtractedEntitiesResponse:
    """
    Extract medical entities from the given text using the PydanticAI agent.

    Args:
        text: The medical text to analyze

    Returns:
        ExtractedEntitiesResponse containing the list of extracted entities

    Raises:
        ValueError: If the text is empty or extraction fails
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    try:
        logger.debug(f"Starting async entity extraction for text: {text[:100]}...")
        agent = get_medical_entity_agent()
        logger.debug("Agent retrieved, calling agent.run()...")
        logger.debug("About to await agent.run()...")
        result = await agent.run(text)
        logger.debug("agent.run() completed, processing result...")
        logger.debug(f"Entity extraction completed, found {len(result.output.entities)} entities")
        return result.output
    except Exception as e:
        logger.error(f"Entity extraction failed: {type(e).__name__}: {e}", exc_info=True)
        raise ValueError(f"Entity extraction failed: {e}") from e


def extract_medical_entities_sync(text: str) -> ExtractedEntitiesResponse:
    """
    Extract medical entities from the given text using the PydanticAI agent (synchronous).

    Args:
        text: The medical text to analyze

    Returns:
        ExtractedEntitiesResponse containing the list of extracted entities

    Raises:
        ValueError: If the text is empty or extraction fails
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    try:
        agent = get_medical_entity_agent()
        result = agent.run_sync(text)
        return result.output
    except Exception as e:
        raise ValueError(f"Entity extraction failed: {e}") from e


# ============================================================================
# Relation Extraction Agent
# ============================================================================


class EntityReference(BaseModel):
    """Reference to an entity for relation extraction."""

    id: int = Field(..., description="Entity ID from the database")
    text: str = Field(..., description="Entity text as it appears in the document")
    entity_type: EntityType = Field(..., description="Type of the entity")


class ExtractedRelation(BaseModel):
    """Represents an extracted relationship between two entities."""

    source_entity_id: int = Field(
        ..., description="ID of the source entity in the relationship"
    )
    target_entity_id: int = Field(
        ..., description="ID of the target entity in the relationship"
    )
    relation_type: RelationType = Field(
        ..., description="Type of relationship between the entities"
    )
    confidence: float = Field(
        default=0.8,
        description="Confidence score for this relation (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )


class ExtractedRelationsResponse(BaseModel):
    """Response containing a list of extracted medical entity relationships."""

    relations: list[ExtractedRelation] = Field(
        default_factory=list, description="List of extracted relationships"
    )


# System prompt for medical relation extraction
MEDICAL_RELATION_SYSTEM_PROMPT = """You are an expert medical knowledge graph builder. Your task \
is to identify meaningful relationships between medical entities in the provided text.

Given a list of entities from a medical document, identify relationships between them based on \
medical knowledge and context from the text.

Relation types available:
- TREATS: A medication/procedure treats a disease or symptom (e.g., "Aspirin treats headache")
- CAUSES: An entity causes another (e.g., "Bacteria causes infection")
- HAS_SYMPTOM: A disease has a symptom (e.g., "Flu has symptom fever")
- INDICATES: A symptom/lab value indicates a disease
        (e.g., "High blood pressure indicates hypertension")
- CONTRAINDICATES: A medication is contraindicated for a condition
        (e.g., "Aspirin contraindicates bleeding disorders")
- DOSAGE_FOR: A dosage amount is for a specific medication (e.g., "500mg dosage_for Amoxicillin")
- LOCATED_IN: An entity is anatomically located in another (e.g., "Tumor located_in lung")
- TEMPORAL: Temporal relationship between entities (e.g., before, after, during)
- OTHER: Any other medically relevant relationship

Guidelines:
1. Only create relationships that are clearly supported by the text or medical knowledge
2. Focus on clinically meaningful relationships
3. Avoid creating redundant or trivial relationships
4. Use appropriate directionality (source -> target matters)
5. Assign confidence scores: 1.0 for explicit relationships in text,
   0.1-0.9 for implied relationships
6. Do not create relationships between entities of incompatible types
   (e.g., don't relate two dosages)

Return all identified relationships in the specified JSON format."""


def create_medical_relation_agent() -> Agent[None, ExtractedRelationsResponse]:
    """
    Create the medical relation extraction agent.

    Returns:
        Agent configured for extracting relationships between medical entities
    """
    logger.debug("Creating medical relation extraction agent...")
    agent = Agent(  # type: ignore[misc]
        model="openai:gpt-5-mini",
        system_prompt=MEDICAL_RELATION_SYSTEM_PROMPT,
        output_type=ExtractedRelationsResponse,
        retries=2,
    )
    logger.debug("Relation agent created successfully")
    return agent


# Create a singleton instance
_medical_relation_agent: Agent[None, ExtractedRelationsResponse] | None = None


def get_medical_relation_agent() -> Agent[None, ExtractedRelationsResponse]:
    """
    Get the singleton instance of the medical relation extraction agent.

    Returns:
        The medical relation extraction agent
    """
    global _medical_relation_agent
    if _medical_relation_agent is None:
        _medical_relation_agent = create_medical_relation_agent()
    return _medical_relation_agent


async def extract_medical_relations(
    text: str, entities: list[EntityReference]
) -> ExtractedRelationsResponse:
    """
    Extract medical relationships from entities in the given text using the PydanticAI agent.

    Args:
        text: The medical text containing the entities
        entities: List of entities to find relationships between

    Returns:
        ExtractedRelationsResponse containing the list of extracted relationships

    Raises:
        ValueError: If entities list is empty or extraction fails
    """
    if not entities:
        raise ValueError("Entities list cannot be empty")

    try:
        logger.debug(
            f"Starting async relation extraction for {len(entities)} entities..."
        )
        agent = get_medical_relation_agent()

        # Build a prompt with entity information
        entity_list = "\n".join(
            [
                f"- Entity {e.id}: '{e.text}' (type: {e.entity_type})"
                for e in entities
            ]
        )
        prompt = f"""Document text:
{text}

Entities identified:
{entity_list}

Identify meaningful medical relationships between these entities
based on the text and medical knowledge."""

        logger.debug("About to await agent.run()...")
        result = await agent.run(prompt)
        logger.debug(
            f"Relation extraction completed, found {len(result.output.relations)} relations"
        )
        return result.output
    except Exception as e:
        logger.error(
            f"Relation extraction failed: {type(e).__name__}: {e}", exc_info=True
        )
        raise ValueError(f"Relation extraction failed: {e}") from e


def extract_medical_relations_sync(
    text: str, entities: list[EntityReference]
) -> ExtractedRelationsResponse:
    """
    Extract medical relationships from entities (synchronous).

    Args:
        text: The medical text containing the entities
        entities: List of entities to find relationships between

    Returns:
        ExtractedRelationsResponse containing the list of extracted relationships

    Raises:
        ValueError: If entities list is empty or extraction fails
    """
    if not entities:
        raise ValueError("Entities list cannot be empty")

    try:
        agent = get_medical_relation_agent()

        # Build a prompt with entity information
        entity_list = "\n".join(
            [
                f"- Entity {e.id}: '{e.text}' (type: {e.entity_type})"
                for e in entities
            ]
        )
        prompt = f"""Document text:
{text}

Entities identified:
{entity_list}

Identify meaningful medical relationships between these entities
based on the text and medical knowledge."""

        result = agent.run_sync(prompt)
        return result.output
    except Exception as e:
        raise ValueError(f"Relation extraction failed: {e}") from e
