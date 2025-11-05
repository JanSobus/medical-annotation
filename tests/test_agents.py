"""Tests for PydanticAI agents."""

import pytest
from pydantic import ValidationError

from src.agents import (
    EntityReference,
    ExtractedEntitiesResponse,
    ExtractedEntity,
    ExtractedRelation,
    ExtractedRelationsResponse,
    create_medical_entity_agent,
    create_medical_relation_agent,
    get_medical_entity_agent,
    get_medical_relation_agent,
)
from src.models.entity import EntityType
from src.models.relation import RelationType


def test_extracted_entity_model() -> None:
    """Test ExtractedEntity model creation and validation."""
    entity = ExtractedEntity(
        text="diabetes",
        entity_type=EntityType.DISEASE,
        start_char=10,
        end_char=18,
        confidence=0.95,
    )

    assert entity.text == "diabetes"
    assert entity.entity_type == EntityType.DISEASE
    assert entity.start_char == 10
    assert entity.end_char == 18
    assert entity.confidence == 0.95


def test_extracted_entity_default_confidence() -> None:
    """Test ExtractedEntity with default confidence value."""
    entity = ExtractedEntity(
        text="fever",
        entity_type=EntityType.SYMPTOM,
        start_char=0,
        end_char=5,
    )

    assert entity.confidence == 1.0


def test_extracted_entity_invalid_confidence() -> None:
    """Test ExtractedEntity with invalid confidence values."""
    # Test confidence > 1.0
    with pytest.raises(ValidationError):
        ExtractedEntity(
            text="test",
            entity_type=EntityType.OTHER,
            start_char=0,
            end_char=4,
            confidence=1.5,
        )

    # Test confidence < 0.0
    with pytest.raises(ValidationError):
        ExtractedEntity(
            text="test",
            entity_type=EntityType.OTHER,
            start_char=0,
            end_char=4,
            confidence=-0.5,
        )


def test_extracted_entities_response_model() -> None:
    """Test ExtractedEntitiesResponse model creation."""
    entity1 = ExtractedEntity(
        text="diabetes",
        entity_type=EntityType.DISEASE,
        start_char=10,
        end_char=18,
        confidence=0.95,
    )
    entity2 = ExtractedEntity(
        text="metformin",
        entity_type=EntityType.MEDICATION,
        start_char=30,
        end_char=39,
        confidence=1.0,
    )

    response = ExtractedEntitiesResponse(
        entities=[entity1, entity2],
        text="Patient has diabetes and takes metformin.",
    )

    assert len(response.entities) == 2
    assert response.text == "Patient has diabetes and takes metformin."
    assert response.entities[0].text == "diabetes"
    assert response.entities[1].text == "metformin"


def test_extracted_entities_response_empty_list() -> None:
    """Test ExtractedEntitiesResponse with empty entities list."""
    response = ExtractedEntitiesResponse(
        entities=[],
        text="No entities found.",
    )

    assert len(response.entities) == 0
    assert response.text == "No entities found."


def test_entity_reference_model() -> None:
    """Test EntityReference model creation."""
    ref = EntityReference(
        id=1,
        text="aspirin",
        entity_type=EntityType.MEDICATION,
    )

    assert ref.id == 1
    assert ref.text == "aspirin"
    assert ref.entity_type == EntityType.MEDICATION


def test_extracted_relation_model() -> None:
    """Test ExtractedRelation model creation and validation."""
    relation = ExtractedRelation(
        source_entity_id=1,
        target_entity_id=2,
        relation_type=RelationType.TREATS,
        confidence=0.9,
    )

    assert relation.source_entity_id == 1
    assert relation.target_entity_id == 2
    assert relation.relation_type == RelationType.TREATS
    assert relation.confidence == 0.9


def test_extracted_relation_default_confidence() -> None:
    """Test ExtractedRelation with default confidence value."""
    relation = ExtractedRelation(
        source_entity_id=1,
        target_entity_id=2,
        relation_type=RelationType.CAUSES,
    )

    assert relation.confidence == 0.8


def test_extracted_relation_invalid_confidence() -> None:
    """Test ExtractedRelation with invalid confidence values."""
    # Test confidence > 1.0
    with pytest.raises(ValidationError):
        ExtractedRelation(
            source_entity_id=1,
            target_entity_id=2,
            relation_type=RelationType.TREATS,
            confidence=1.5,
        )

    # Test confidence < 0.0
    with pytest.raises(ValidationError):
        ExtractedRelation(
            source_entity_id=1,
            target_entity_id=2,
            relation_type=RelationType.TREATS,
            confidence=-0.5,
        )


def test_extracted_relations_response_model() -> None:
    """Test ExtractedRelationsResponse model creation."""
    relation1 = ExtractedRelation(
        source_entity_id=1,
        target_entity_id=2,
        relation_type=RelationType.TREATS,
        confidence=0.9,
    )
    relation2 = ExtractedRelation(
        source_entity_id=3,
        target_entity_id=4,
        relation_type=RelationType.INDICATES,
        confidence=0.85,
    )

    response = ExtractedRelationsResponse(
        relations=[relation1, relation2],
    )

    assert len(response.relations) == 2
    assert response.relations[0].relation_type == RelationType.TREATS
    assert response.relations[1].relation_type == RelationType.INDICATES


def test_extracted_relations_response_empty_list() -> None:
    """Test ExtractedRelationsResponse with empty relations list."""
    response = ExtractedRelationsResponse(relations=[])

    assert len(response.relations) == 0


def test_create_medical_entity_agent() -> None:
    """Test creating a medical entity extraction agent."""
    agent = create_medical_entity_agent()

    assert agent is not None


def test_get_medical_entity_agent_singleton() -> None:
    """Test that get_medical_entity_agent returns the same instance."""
    agent1 = get_medical_entity_agent()
    agent2 = get_medical_entity_agent()

    # Should return the same instance (singleton pattern)
    assert agent1 is agent2


def test_create_medical_relation_agent() -> None:
    """Test creating a medical relation extraction agent."""
    agent = create_medical_relation_agent()

    assert agent is not None


def test_get_medical_relation_agent_singleton() -> None:
    """Test that get_medical_relation_agent returns the same instance."""
    agent1 = get_medical_relation_agent()
    agent2 = get_medical_relation_agent()

    # Should return the same instance (singleton pattern)
    assert agent1 is agent2


def test_entity_types_coverage() -> None:
    """Test that all EntityType values can be used in ExtractedEntity."""
    for entity_type in EntityType:
        entity = ExtractedEntity(
            text="test",
            entity_type=entity_type,
            start_char=0,
            end_char=4,
        )
        assert entity.entity_type == entity_type


def test_relation_types_coverage() -> None:
    """Test that all RelationType values can be used in ExtractedRelation."""
    for relation_type in RelationType:
        relation = ExtractedRelation(
            source_entity_id=1,
            target_entity_id=2,
            relation_type=relation_type,
        )
        assert relation.relation_type == relation_type


def test_extracted_entity_character_positions() -> None:
    """Test ExtractedEntity with various character positions."""
    # Test with start_char = 0
    entity1 = ExtractedEntity(
        text="fever",
        entity_type=EntityType.SYMPTOM,
        start_char=0,
        end_char=5,
    )
    assert entity1.start_char == 0
    assert entity1.end_char == 5

    # Test with large positions
    entity2 = ExtractedEntity(
        text="test",
        entity_type=EntityType.OTHER,
        start_char=1000,
        end_char=1004,
    )
    assert entity2.start_char == 1000
    assert entity2.end_char == 1004


def test_extracted_entity_negative_positions() -> None:
    """Test that ExtractedEntity rejects negative character positions."""
    with pytest.raises(ValidationError):
        ExtractedEntity(
            text="test",
            entity_type=EntityType.OTHER,
            start_char=-1,
            end_char=4,
        )


def test_entity_reference_all_types() -> None:
    """Test EntityReference with all entity types."""
    for i, entity_type in enumerate(EntityType):
        ref = EntityReference(
            id=i,
            text=f"entity_{i}",
            entity_type=entity_type,
        )
        assert ref.id == i
        assert ref.entity_type == entity_type


def test_extracted_entities_response_with_multiple_types() -> None:
    """Test ExtractedEntitiesResponse with entities of different types."""
    entities = [
        ExtractedEntity(
            text="diabetes",
            entity_type=EntityType.DISEASE,
            start_char=0,
            end_char=8,
        ),
        ExtractedEntity(
            text="metformin",
            entity_type=EntityType.MEDICATION,
            start_char=10,
            end_char=19,
        ),
        ExtractedEntity(
            text="fever",
            entity_type=EntityType.SYMPTOM,
            start_char=21,
            end_char=26,
        ),
        ExtractedEntity(
            text="blood test",
            entity_type=EntityType.PROCEDURE,
            start_char=28,
            end_char=38,
        ),
    ]

    response = ExtractedEntitiesResponse(
        entities=entities,
        text="diabetes, metformin, fever, blood test",
    )

    assert len(response.entities) == 4
    assert response.entities[0].entity_type == EntityType.DISEASE
    assert response.entities[1].entity_type == EntityType.MEDICATION
    assert response.entities[2].entity_type == EntityType.SYMPTOM
    assert response.entities[3].entity_type == EntityType.PROCEDURE


def test_extracted_relations_response_with_multiple_types() -> None:
    """Test ExtractedRelationsResponse with relations of different types."""
    relations = [
        ExtractedRelation(
            source_entity_id=1,
            target_entity_id=2,
            relation_type=RelationType.TREATS,
        ),
        ExtractedRelation(
            source_entity_id=3,
            target_entity_id=4,
            relation_type=RelationType.CAUSES,
        ),
        ExtractedRelation(
            source_entity_id=5,
            target_entity_id=6,
            relation_type=RelationType.HAS_SYMPTOM,
        ),
        ExtractedRelation(
            source_entity_id=7,
            target_entity_id=8,
            relation_type=RelationType.INDICATES,
        ),
    ]

    response = ExtractedRelationsResponse(relations=relations)

    assert len(response.relations) == 4
    assert response.relations[0].relation_type == RelationType.TREATS
    assert response.relations[1].relation_type == RelationType.CAUSES
    assert response.relations[2].relation_type == RelationType.HAS_SYMPTOM
    assert response.relations[3].relation_type == RelationType.INDICATES

