import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.pipeline.llm_client import llm_client
from app.pipeline.parsers.extraction_parser import parse_and_validate_extraction
from app.pipeline.resolution.entity_resolution import cluster_mentions
from app.utils.text_splitter import chunk_text
from app.config.logging import get_logger

logger = get_logger(__name__)

PROMPT_FILE = Path(__file__).parent / "prompts" / "extraction_prompt.txt"

def load_system_prompt() -> str:
    if PROMPT_FILE.exists():
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "Extract structured entities, relationships, and events into strict JSON."


class ExtractionOrchestrator:
    def __init__(self):
        self.system_prompt = load_system_prompt()

    def extract_chapter(
        self,
        chapter_text: str,
        chapter_number: int = 1,
        progress_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Processes a full chapter's text: chunks it, sends to LLM, parses,
        and aggregates entities, relationships, and events.
        """
        chunks = chunk_text(chapter_text, max_chars=8000, overlap=400)
        logger.info(f"Chapter {chapter_number}: split into {len(chunks)} chunks for extraction.")

        all_raw_entities: List[Dict[str, Any]] = []
        all_relationships: List[Dict[str, Any]] = []
        all_events: List[Dict[str, Any]] = []
        all_state_changes: List[Dict[str, Any]] = []
        all_temporal_relations: List[Dict[str, Any]] = []

        for idx, chunk in enumerate(chunks):
            chunk_prompt = (
                f"Extract structured world state information from the following passage.\n\n"
                f"CHUNK [{idx + 1}/{len(chunks)}]:\n"
                f"-----------------------------------------\n"
                f"{chunk['text']}\n"
                f"-----------------------------------------\n"
                f"Output strictly valid JSON matching the instructions."
            )

            raw_output = llm_client.generate(
                prompt=chunk_prompt,
                system_prompt=self.system_prompt,
                json_mode=True,
                temperature=0.0
            )

            parsed, errors = parse_and_validate_extraction(raw_output)
            if errors:
                logger.warning(f"Chunk {idx + 1} validation warnings: {errors}")

            # Collect items with provenance
            for ent in parsed["entities"]:
                ent["source_chunk"] = chunk["chunk_id"]
                all_raw_entities.append(ent)

            for rel in parsed["relationships"]:
                rel["source_chunk"] = chunk["chunk_id"]
                all_relationships.append(rel)

            for ev in parsed["events"]:
                ev["source_chunk"] = chunk["chunk_id"]
                all_events.append(ev)

            all_state_changes.extend(parsed.get("state_changes", []))
            all_temporal_relations.extend(parsed.get("temporal_relations", []))

            if progress_callback:
                progress_callback(idx + 1, len(chunks))

        # Cluster duplicate entities across chunks
        clustered_entities = cluster_mentions(all_raw_entities)

        return {
            "chapter_number": chapter_number,
            "entities": clustered_entities,
            "raw_mentions": all_raw_entities,
            "relationships": all_relationships,
            "events": all_events,
            "state_changes": all_state_changes,
            "temporal_relations": all_temporal_relations
        }

# Global instance
orchestrator = ExtractionOrchestrator()
