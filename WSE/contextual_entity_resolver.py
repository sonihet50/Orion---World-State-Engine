"""Conservative, local-LLM resolution for ambiguous entity references."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from extractor import MODEL_NAME, post_ollama


CONTEXTUAL_CONFIDENCE_THRESHOLD = 0.95

CONTEXTUAL_RESOLUTION_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {
            "type": "string",
            "enum": ["MATCH", "NEW_ENTITY", "UNRESOLVED"],
        },
        "entity_id": {"type": ["string", "null"]},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string"},
    },
    "required": ["decision", "entity_id", "confidence", "reason"],
}

SYSTEM_PROMPT = """
You are the contextual entity-resolution module of the World State Engine.
Decide whether one ambiguous narrative mention identifies one of the supplied
candidate entities. Use only the supplied structured context. Be conservative:
when context does not clearly support an identity, return UNRESOLVED.

Return MATCH only when evidence supports the identity with high confidence.
For MATCH, entity_id MUST be exactly one supplied candidate entity ID. Never
invent an entity ID. For NEW_ENTITY and UNRESOLVED, entity_id must be null.
If no candidates are supplied, return UNRESOLVED unless the mention itself
clearly establishes a distinct named entity. A generic description or initials
without enough context must be UNRESOLVED, not a guess.
Return only JSON that conforms to the supplied schema.
"""


class ContextualEntityResolver:
    """Calls the existing local Ollama model for one ambiguous mention."""

    def resolve(
        self,
        mention: Dict[str, Any],
        candidates: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        allowed_ids = {candidate["entity_id"] for candidate in candidates}
        prompt = {
            "ambiguous_mention": mention,
            "candidate_entities": candidates,
            "rules": {
                "match_only_from_candidate_entities": True,
                "prefer_unresolved_when_context_is_insufficient": True,
            },
        }
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
            "stream": False,
            "format": CONTEXTUAL_RESOLUTION_SCHEMA,
            "options": {"temperature": 0},
        }

        try:
            result = json.loads(post_ollama(payload)["message"]["content"])
        except (
            KeyError,
            TypeError,
            ValueError,
            RuntimeError,
        ) as error:
            return self._unresolved(
                "Local contextual resolution was unavailable: "
                f"{type(error).__name__}."
            )

        return self._validate_result(result, allowed_ids)

    def _validate_result(
        self,
        result: Any,
        allowed_ids: set[str],
    ) -> Dict[str, Any]:
        if not isinstance(result, dict):
            return self._unresolved("The local model returned an invalid result.")

        decision = result.get("decision")
        entity_id = result.get("entity_id")
        confidence = result.get("confidence")
        reason = str(result.get("reason") or "No reason supplied.")

        if not isinstance(confidence, (int, float)):
            return self._unresolved("The local model omitted a numeric confidence.")

        confidence = max(0.0, min(1.0, float(confidence)))
        if (
            decision == "MATCH"
            and entity_id in allowed_ids
            and confidence >= CONTEXTUAL_CONFIDENCE_THRESHOLD
        ):
            return {
                "decision": "MATCH",
                "entity_id": entity_id,
                "confidence": confidence,
                "reason": reason,
            }
        if decision == "NEW_ENTITY":
            return {
                "decision": "NEW_ENTITY",
                "entity_id": None,
                "confidence": confidence,
                "reason": reason,
            }

        # Invalid IDs, low-confidence matches, and malformed decisions are
        # deliberately downgraded to UNRESOLVED rather than merged.
        return self._unresolved(reason, confidence)

    @staticmethod
    def _unresolved(reason: str, confidence: float = 0.0) -> Dict[str, Any]:
        return {
            "decision": "UNRESOLVED",
            "entity_id": None,
            "confidence": confidence,
            "reason": reason,
        }
