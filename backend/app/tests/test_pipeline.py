import pytest
from app.utils.text_splitter import split_into_chapters, chunk_text
from app.pipeline.parsers.extraction_parser import parse_and_validate_extraction, clean_json_response
from app.pipeline.resolution.entity_resolution import (
    normalize_name,
    token_similarity,
    calculate_match_confidence,
    cluster_mentions
)
from app.pipeline.resolution.fact_resolution import resolve_fact_update
from app.pipeline.resolution.relationship_resolution import resolve_relationship_update
from app.core.constants import FactStatus, RelationshipStatus

def test_split_into_chapters():
    text = (
        "Chapter 1: The Beginning\n"
        "It was the best of times.\n\n"
        "Chapter 2: The Middle\n"
        "Things began to shift."
    )
    chapters = split_into_chapters(text)
    assert len(chapters) == 2
    assert chapters[0][0] == 1
    assert "Beginning" in chapters[0][1]
    assert chapters[1][0] == 2
    assert "Middle" in chapters[1][1]

def test_split_into_chapters_fallback():
    text = "Just a short story with no chapter heading whatsoever."
    chapters = split_into_chapters(text)
    assert len(chapters) == 1
    assert chapters[0][0] == 1
    assert chapters[0][2] == text

def test_chunk_text():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = chunk_text(text, max_chars=30, overlap=5)
    assert len(chunks) >= 1
    assert all("chunk_id" in c for c in chunks)

def test_clean_json_response():
    raw = "```json\n{\"entities\": [], \"relationships\": []}\n```"
    cleaned = clean_json_response(raw)
    assert cleaned.startswith("{")
    assert cleaned.endswith("}")

def test_parse_and_validate_extraction():
    raw = """
    {
      "entities": [
        {
          "canonical_name": "Alice Sterling",
          "mention": "Alice",
          "type": "character",
          "attributes": {"rank": "Captain"}
        }
      ],
      "relationships": [
        {
          "subject": "Alice Sterling",
          "predicate": "COMMANDS",
          "object": "USS Enterprise"
        }
      ],
      "events": []
    }
    """
    parsed, errors = parse_and_validate_extraction(raw)
    assert len(errors) == 0
    assert len(parsed["entities"]) == 1
    assert parsed["entities"][0]["canonical_name"] == "Alice Sterling"
    assert len(parsed["relationships"]) == 1
    assert parsed["relationships"][0]["predicate"] == "COMMANDS"

def test_cluster_mentions():
    mentions = [
        {"canonical_name": "Alice Sterling", "mention": "Alice", "type": "character", "attributes": {"age": "30"}},
        {"canonical_name": "Alice", "mention": "Captain Alice", "type": "character", "attributes": {"rank": "Captain"}}
    ]
    clusters = cluster_mentions(mentions)
    assert len(clusters) == 1
    assert clusters[0]["canonical_name"] == "Alice Sterling"
    assert "Alice" in clusters[0]["aliases"] or "Captain Alice" in clusters[0]["aliases"]
    assert clusters[0]["attributes"].get("rank") == "Captain"

def test_resolve_fact_update_no_change():
    status, con = resolve_fact_update("rank", "Captain", "Captain")
    assert status == FactStatus.ACTIVE.value
    assert con is None

def test_resolve_fact_update_contradiction():
    # eye_color is immutable -> contradiction
    status, con = resolve_fact_update("eye_color", "blue", "green", "Alice")
    assert status == FactStatus.CONTRADICTED.value
    assert con is not None
    assert "blue" in con["explanation"] and "green" in con["explanation"]

def test_resolve_relationship_update_conflict():
    status, con = resolve_relationship_update("ENEMY_OF", "FRIEND_OF", "Alice", "Bob")
    assert status == RelationshipStatus.CONTRADICTED.value
    assert con is not None
