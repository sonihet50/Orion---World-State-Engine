# entity_resolver.py

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

from contextual_entity_resolver import ContextualEntityResolver


# ============================================================
# CONFIGURATION
# ============================================================

# Score required for an automatic fuzzy/deterministic merge.
FUZZY_MERGE_THRESHOLD = 0.90

# Score required before a possible candidate is recorded.
CANDIDATE_THRESHOLD = 0.55

# Maximum number of candidates retained for an ambiguous mention.
MAX_CANDIDATES = 3


# ============================================================
# ENTITY TYPE NORMALIZATION
# ============================================================

TYPE_NORMALIZATION = {
    # Character / person
    "person": "CHARACTER",
    "PERSON": "CHARACTER",
    "character": "CHARACTER",
    "CHARACTER": "CHARACTER",

    # Location
    "location": "LOCATION",
    "LOCATION": "LOCATION",
    "place": "LOCATION",
    "PLACE": "LOCATION",

    # Organization
    "organization": "ORGANIZATION",
    "ORGANIZATION": "ORGANIZATION",
    "org": "ORGANIZATION",
    "ORG": "ORGANIZATION",

    # Vehicle
    "vehicle": "VEHICLE",
    "VEHICLE": "VEHICLE",

    # Game
    "game": "GAME",
    "GAME": "GAME",

    # Object
    "object": "OBJECT",
    "OBJECT": "OBJECT",

    # Mythological entities
    "mythological_entity": "MYTHOLOGICAL_ENTITY",
    "MYTHOLOGICAL_ENTITY": "MYTHOLOGICAL_ENTITY",
    "mythological entity": "MYTHOLOGICAL_ENTITY",
    "MYTHOLOGICAL ENTITY": "MYTHOLOGICAL_ENTITY",

    # Generic entity
    "entity": "ENTITY",
    "ENTITY": "ENTITY",
}


def normalize_entity_type(entity_type: Optional[str]) -> str:
    """
    Normalize extracted entity types into the canonical WSE vocabulary.

    Examples:
        PERSON -> CHARACTER
        person -> CHARACTER
        Character -> CHARACTER
        PLACE -> LOCATION
    """

    if not entity_type:
        return "ENTITY"

    value = str(entity_type).strip()

    if value in TYPE_NORMALIZATION:
        return TYPE_NORMALIZATION[value]

    lower_value = value.lower()

    if lower_value in TYPE_NORMALIZATION:
        return TYPE_NORMALIZATION[lower_value]

    return value.upper()


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: Optional[str]) -> str:
    """
    Normalize a name/mention for comparison.

    This is intentionally conservative.
    We remove punctuation differences and normalize whitespace,
    but we do not remove meaningful words.
    """

    if not text:
        return ""

    text = str(text).strip().lower()

    # Normalize apostrophes and dashes.
    text = text.replace("’", "'")
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Remove common punctuation.
    text = re.sub(r"[^\w\s-]", " ", text)

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text


def compact_text(text: Optional[str]) -> str:
    """
    More aggressive normalization used only for exact comparison.
    """

    normalized = normalize_text(text)
    return normalized.replace(" ", "").replace("-", "")


def tokenize_name(text: Optional[str]) -> List[str]:
    normalized = normalize_text(text)

    if not normalized:
        return []

    return normalized.split()


# ============================================================
# NAME / ALIAS HELPERS
# ============================================================

def is_title_word(word: str) -> bool:
    return word.lower().rstrip(".") in {
        "mr",
        "mrs",
        "ms",
        "miss",
        "dr",
        "prof",
        "sir",
        "lady",
        "lord",
    }


def remove_title(text: str) -> str:
    """
    Remove a leading honorific.

    Example:
        'Mr Sato' -> 'Sato'
        'Dr Alice Sharma' -> 'Alice Sharma'
    """

    tokens = tokenize_name(text)

    while tokens and is_title_word(tokens[0]):
        tokens.pop(0)

    return " ".join(tokens)


def is_description_like(text: str) -> bool:
    """
    Detect generic narrative descriptions that should not be
    automatically merged through fuzzy matching.

    Examples:
        'the woman'
        'the owner'
        'the man'
        'a man'
    """

    normalized = normalize_text(text)

    description_patterns = [
        r"^(the|a|an)\s+(man|woman|person|owner|girl|boy|lady|gentleman)$",
        r"^(the|a|an)\s+(driver|passenger|farmer|doctor|teacher|student)$",
        r"^(the|a|an)\s+\w+$",
    ]

    return any(
        re.match(pattern, normalized)
        for pattern in description_patterns
    )


# ============================================================
# SIMILARITY
# ============================================================

def sequence_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        normalize_text(a),
        normalize_text(b),
    ).ratio()


def token_overlap(a: str, b: str) -> float:
    tokens_a = set(tokenize_name(a))
    tokens_b = set(tokenize_name(b))

    if not tokens_a or not tokens_b:
        return 0.0

    intersection = tokens_a.intersection(tokens_b)

    return len(intersection) / max(
        len(tokens_a),
        len(tokens_b),
    )


def name_similarity(
    mention: str,
    candidate: str,
) -> float:
    """
    Calculate a conservative name similarity.

    The maximum of several signals is used because:
      Robert J. Guthard
      Rob Guthard

    may have lower raw character similarity than expected,
    while token relationships can still provide useful evidence.
    """

    mention_norm = normalize_text(mention)
    candidate_norm = normalize_text(candidate)

    if not mention_norm or not candidate_norm:
        return 0.0

    # Exact normalized match.
    if mention_norm == candidate_norm:
        return 1.0

    # Compact exact match.
    if compact_text(mention) == compact_text(candidate):
        return 0.99

    sequence_score = sequence_similarity(
        mention_norm,
        candidate_norm,
    )

    overlap_score = token_overlap(
        mention_norm,
        candidate_norm,
    )

    # Containment.
    containment_score = 0.0

    if (
        mention_norm in candidate_norm
        or candidate_norm in mention_norm
    ):
        shorter = min(
            len(mention_norm),
            len(candidate_norm),
        )
        longer = max(
            len(mention_norm),
            len(candidate_norm),
        )

        if longer > 0:
            containment_score = shorter / longer

    return max(
        sequence_score,
        overlap_score,
        containment_score,
    )


def has_compatible_first_name(
    first_name_a: str,
    first_name_b: str,
) -> bool:
    """Return whether one non-initial first name is a clear prefix of the other."""

    a = normalize_text(first_name_a)
    b = normalize_text(first_name_b)

    return (
        len(a) >= 3
        and len(b) >= 3
        and (a.startswith(b) or b.startswith(a))
    )


# ============================================================
# ENTITY RESOLVER
# ============================================================

class EntityResolver:
    """
    Deterministic entity resolver for WSE.

    Responsibilities:
        1. Normalize entity types.
        2. Maintain canonical entities.
        3. Maintain aliases.
        4. Resolve obvious aliases deterministically.
        5. Generate candidates for ambiguous mentions.
        6. Preserve provenance.

    The resolver deliberately does NOT perform LLM reasoning yet.
    """

    def __init__(self) -> None:
        self.entities: Dict[str, Dict[str, Any]] = {}

        # Fast alias index:
        #
        #   (normalized_alias, normalized_type)
        #       -> entity_id
        #
        self.alias_index: Dict[Tuple[str, str], str] = {}

        # Per-type counters.
        self.type_counters: Dict[str, int] = {}

        self.contextual_resolver = ContextualEntityResolver()

    # --------------------------------------------------------
    # ID GENERATION
    # --------------------------------------------------------

    def _next_entity_id(self, entity_type: str) -> str:
        current = self.type_counters.get(entity_type, 0) + 1
        self.type_counters[entity_type] = current

        return f"{entity_type}_{current:03d}"

    # --------------------------------------------------------
    # ALIAS INDEX
    # --------------------------------------------------------

    def _index_alias(
        self,
        alias: str,
        entity_type: str,
        entity_id: str,
    ) -> None:

        normalized_alias = normalize_text(alias)

        if not normalized_alias:
            return

        key = (
            normalized_alias,
            entity_type,
        )

        self.alias_index[key] = entity_id

    def _index_entity_aliases(
        self,
        entity: Dict[str, Any],
    ) -> None:

        entity_id = entity["entity_id"]
        entity_type = entity["type"]

        self._index_alias(
            entity["canonical_name"],
            entity_type,
            entity_id,
        )

        for alias in entity.get("aliases", []):
            self._index_alias(
                alias,
                entity_type,
                entity_id,
            )

    # --------------------------------------------------------
    # ENTITY CREATION
    # --------------------------------------------------------

    def _create_entity(
        self,
        mention: str,
        canonical_name: str,
        entity_type: str,
        attributes: Optional[Dict[str, Any]],
        evidence: Optional[str],
        chunk_id: Optional[str],
    ) -> Dict[str, Any]:

        entity_id = self._next_entity_id(entity_type)

        entity = {
            "entity_id": entity_id,
            "canonical_name": canonical_name,
            "type": entity_type,
            "aliases": [],
            "attributes": attributes or {},
            "provenance": [],
        }

        # The canonical name is always its own alias.
        self._add_alias(
            entity,
            canonical_name,
        )

        # Add the extracted mention if different.
        if normalize_text(mention) != normalize_text(canonical_name):
            self._add_alias(
                entity,
                mention,
            )

        # First provenance record.
        self._add_provenance(
            entity=entity,
            mention=mention,
            chunk_id=chunk_id,
            evidence=evidence,
        )

        self.entities[entity_id] = entity

        self._index_entity_aliases(entity)

        return entity

    # --------------------------------------------------------
    # ALIAS MANAGEMENT
    # --------------------------------------------------------

    def _add_alias(
        self,
        entity: Dict[str, Any],
        alias: Optional[str],
    ) -> None:

        if not alias:
            return

        alias = str(alias).strip()

        if not alias:
            return

        normalized_alias = normalize_text(alias)

        existing_normalized = {
            normalize_text(existing)
            for existing in entity.get("aliases", [])
        }

        if normalized_alias not in existing_normalized:
            entity.setdefault("aliases", []).append(alias)

    # --------------------------------------------------------
    # PROVENANCE
    # --------------------------------------------------------

    def _add_provenance(
        self,
        entity: Dict[str, Any],
        mention: str,
        chunk_id: Optional[str],
        evidence: Optional[str],
    ) -> None:

        # IMPORTANT:
        # Always use the canonical_name of the RESOLVED entity.
        #
        # Do not copy the incoming extraction's canonical_name here.
        #
        # This fixes:
        #
        #   Rob -> Rob
        #
        # becoming:
        #
        #   Rob -> Robert J. Guthard

        provenance_record = {
            "chunk_id": chunk_id,
            "mention": mention,
            "canonical_name": entity["canonical_name"],
        }

        if evidence:
            provenance_record["evidence"] = evidence

        entity.setdefault(
            "provenance",
            [],
        ).append(provenance_record)

    # --------------------------------------------------------
    # EXACT ALIAS MATCH
    # --------------------------------------------------------

    def _exact_alias_match(
        self,
        mention: str,
        entity_type: str,
    ) -> Optional[Dict[str, Any]]:

        normalized_mention = normalize_text(mention)

        if not normalized_mention:
            return None

        key = (
            normalized_mention,
            entity_type,
        )

        entity_id = self.alias_index.get(key)

        if entity_id:
            return self.entities.get(entity_id)

        return None

    # --------------------------------------------------------
    # DETERMINISTIC NAME MATCH
    # --------------------------------------------------------

    def _deterministic_match(
        self,
        mention: str,
        entity_type: str,
    ) -> Tuple[Optional[Dict[str, Any]], float]:

        mention_norm = normalize_text(mention)

        if not mention_norm:
            return None, 0.0

        # Generic descriptions should not be automatically
        # resolved against character names.
        if is_description_like(mention):
            return None, 0.0

        mention_without_title = remove_title(mention)

        best_entity = None
        best_score = 0.0

        for entity in self.entities.values():

            if entity["type"] != entity_type:
                continue

            candidate_names = [
                entity["canonical_name"],
                *entity.get("aliases", []),
            ]

            for candidate in candidate_names:

                candidate_without_title = remove_title(candidate)

                # Exact after title removal.
                if (
                    normalize_text(mention_without_title)
                    == normalize_text(candidate_without_title)
                    and len(tokenize_name(mention_without_title)) >= 2
                ):
                    return entity, 0.98

                score = name_similarity(
                    mention_without_title,
                    candidate_without_title,
                )

                # First-name / surname relationship.
                mention_tokens = tokenize_name(
                    mention_without_title
                )
                candidate_tokens = tokenize_name(
                    candidate_without_title
                )

                if (
                    len(mention_tokens) == 1
                    and len(candidate_tokens) >= 2
                    and mention_tokens[0] in candidate_tokens
                ):
                    score = max(score, 0.94)

                if (
                    len(mention_tokens) == 2
                    and len(candidate_tokens) >= 2
                    and set(mention_tokens).issubset(
                        set(candidate_tokens)
                    )
                ):
                    score = max(score, 0.96)

                # Obvious short-form first names with the same surname,
                # for example "Rob Guthard" and "Robert J. Guthard".
                # A shared surname prevents this from merging a lone
                # nickname such as "Rob" with an unrelated Robert.
                if (
                    len(mention_tokens) >= 2
                    and len(candidate_tokens) >= 2
                    and mention_tokens[-1] == candidate_tokens[-1]
                    and has_compatible_first_name(
                        mention_tokens[0],
                        candidate_tokens[0],
                    )
                ):
                    score = max(score, 0.95)

                if score > best_score:
                    best_score = score
                    best_entity = entity

        if best_score >= FUZZY_MERGE_THRESHOLD:
            return best_entity, best_score

        return None, best_score

    # --------------------------------------------------------
    # CANDIDATE GENERATION
    # --------------------------------------------------------

    def _generate_candidates(
        self,
        mention: str,
        entity_type: str,
    ) -> List[Dict[str, Any]]:

        candidates: List[Dict[str, Any]] = []

        # Generic descriptions are deliberately not matched.
        if is_description_like(mention):
            return candidates

        for entity in self.entities.values():

            if entity["type"] != entity_type:
                continue

            best_score = 0.0

            names = [
                entity["canonical_name"],
                *entity.get("aliases", []),
            ]

            for name in names:
                score = name_similarity(
                    mention,
                    name,
                )

                best_score = max(
                    best_score,
                    score,
                )

            if best_score >= CANDIDATE_THRESHOLD:

                candidates.append(
                    {
                        "entity_id": entity["entity_id"],
                        "canonical_name": entity["canonical_name"],
                        "type": entity["type"],
                        "score": round(
                            best_score,
                            4,
                        ),
                    }
                )

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return candidates[:MAX_CANDIDATES]

    def _requires_contextual_resolution(
        self,
        mention: str,
        canonical_name: str,
    ) -> bool:
        """Limit LLM calls to references deterministic matching cannot judge."""

        if is_description_like(mention) or is_description_like(canonical_name):
            return True

        compact_mention = compact_text(mention)
        return (
            len(compact_mention) <= 3
            and compact_mention.isalpha()
            and mention.isupper()
        )

    def _contextual_candidates(
        self,
        entity_type: str,
        deterministic_candidates: List[Dict[str, Any]],
        evidence: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Build an evidence-supported entity-ID whitelist for the LLM."""

        candidate_ids = {
            candidate["entity_id"]
            for candidate in deterministic_candidates
        }

        normalized_evidence = normalize_text(evidence)
        for entity in self.entities.values():
            if entity["type"] != entity_type:
                continue

            # A candidate is relevant when the same extracted narrative
            # evidence already supports it. This lets "the woman" be compared
            # with Greywoman while preventing unrelated character IDs from
            # being offered for initials or a shop owner.
            for provenance in entity.get("provenance", []):
                if (
                    normalized_evidence
                    and normalize_text(provenance.get("evidence"))
                    == normalized_evidence
                ):
                    candidate_ids.add(entity["entity_id"])
                    break

        candidates = []
        for entity_id in candidate_ids:
            entity = self.entities[entity_id]
            candidates.append(
                {
                    "entity_id": entity["entity_id"],
                    "canonical_name": entity["canonical_name"],
                    "type": entity["type"],
                    "aliases": entity.get("aliases", []),
                    "attributes": entity.get("attributes", {}),
                    "recent_provenance": entity.get("provenance", [])[-3:],
                }
            )

        return sorted(candidates, key=lambda item: item["entity_id"])

    # --------------------------------------------------------
    # RESOLVE ONE ENTITY
    # --------------------------------------------------------

    def resolve_entity(
        self,
        extracted_entity: Dict[str, Any],
        chunk_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        mention = str(
            extracted_entity.get(
                "mention",
                "",
            )
        ).strip()

        canonical_name = str(
            extracted_entity.get(
                "canonical_name",
                mention,
            )
        ).strip()

        entity_type = normalize_entity_type(
            extracted_entity.get("type")
        )

        attributes = extracted_entity.get(
            "attributes",
            {},
        )

        evidence = extracted_entity.get(
            "evidence"
        )

        # ----------------------------------------------------
        # 1. Exact alias
        # ----------------------------------------------------

        entity = self._exact_alias_match(
            mention,
            entity_type,
        )

        if entity is None:
            entity = self._exact_alias_match(
                canonical_name,
                entity_type,
            )

        if entity is not None:

            self._add_alias(
                entity,
                mention,
            )

            self._add_alias(
                entity,
                canonical_name,
            )

            self._add_provenance(
                entity=entity,
                mention=mention,
                chunk_id=chunk_id,
                evidence=evidence,
            )

            self._merge_attributes(
                entity,
                attributes,
            )

            self._index_entity_aliases(entity)

            return {
                "mention": mention,
                "canonical_name": entity["canonical_name"],
                "type": entity["type"],
                "chunk_id": chunk_id,
                "entity_id": entity["entity_id"],
                "resolution_candidates": [],
                "resolution": {
                    "method": "exact_alias",
                    "score": 1.0,
                },
            }

        # ----------------------------------------------------
        # 2. Deterministic strong match
        # ----------------------------------------------------

        entity, deterministic_score = self._deterministic_match(
            mention,
            entity_type,
        )

        if entity is None:
            entity, canonical_score = self._deterministic_match(
                canonical_name,
                entity_type,
            )

            deterministic_score = max(
                deterministic_score,
                canonical_score,
            )

        if entity is not None:

            self._add_alias(
                entity,
                mention,
            )

            self._add_alias(
                entity,
                canonical_name,
            )

            self._add_provenance(
                entity=entity,
                mention=mention,
                chunk_id=chunk_id,
                evidence=evidence,
            )

            self._merge_attributes(
                entity,
                attributes,
            )

            self._index_entity_aliases(entity)

            return {
                "mention": mention,
                "canonical_name": entity["canonical_name"],
                "type": entity["type"],
                "chunk_id": chunk_id,
                "entity_id": entity["entity_id"],
                "resolution_candidates": [],
                "resolution": {
                    "method": "deterministic_alias",
                    "score": round(
                        deterministic_score,
                        4,
                    ),
                },
            }

        # ----------------------------------------------------
        # 3. Candidate generation
        # ----------------------------------------------------

        candidates = self._generate_candidates(
            mention,
            entity_type,
        )

        # ----------------------------------------------------
        # 4. Defer genuinely ambiguous references to the local LLM.
        # ----------------------------------------------------

        if self._requires_contextual_resolution(mention, canonical_name):
            return {
                "mention": mention,
                "canonical_name": canonical_name or mention,
                "type": entity_type,
                "chunk_id": chunk_id,
                "entity_id": None,
                "resolution_candidates": candidates,
                "_contextual_input": {
                    "attributes": attributes,
                    "evidence": evidence,
                },
                "resolution": {
                    "method": "contextual_pending",
                    "score": 0.0,
                },
            }

        # ----------------------------------------------------
        # 5. Create a non-ambiguous new entity.
        # ----------------------------------------------------

        entity = self._create_entity(
            mention=mention,
            canonical_name=canonical_name or mention,
            entity_type=entity_type,
            attributes=attributes,
            evidence=evidence,
            chunk_id=chunk_id,
        )

        return {
            "mention": mention,
            "canonical_name": entity["canonical_name"],
            "type": entity["type"],
            "chunk_id": chunk_id,
            "resolution_candidates": candidates,
            "entity_id": entity["entity_id"],
            "resolution": {
                "method": "new_entity",
                "score": 0.0,
            },
        }

    # --------------------------------------------------------
    # CONTEXTUAL RESOLUTION
    # --------------------------------------------------------

    def _resolve_contextual_mentions(
        self,
        mentions: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        stats = {
            "sent": 0,
            "match": 0,
            "new_entity": 0,
            "unresolved": 0,
        }

        for resolved in mentions:
            if resolved["resolution"]["method"] != "contextual_pending":
                continue

            stats["sent"] += 1
            contextual_input = resolved.pop("_contextual_input")
            candidates = self._contextual_candidates(
                resolved["type"],
                resolved["resolution_candidates"],
                contextual_input["evidence"],
            )
            decision = self.contextual_resolver.resolve(
                {
                    "mention": resolved["mention"],
                    "canonical_name": resolved["canonical_name"],
                    "type": resolved["type"],
                    "chunk_id": resolved["chunk_id"],
                    "evidence": contextual_input["evidence"],
                    "attributes": contextual_input["attributes"],
                    "deterministic_candidates": resolved["resolution_candidates"],
                },
                candidates,
            )

            if decision["decision"] == "MATCH":
                entity = self.entities[decision["entity_id"]]
                self._add_alias(entity, resolved["mention"])
                self._add_alias(entity, resolved["canonical_name"])
                self._add_provenance(
                    entity,
                    resolved["mention"],
                    resolved["chunk_id"],
                    contextual_input["evidence"],
                )
                self._merge_attributes(entity, contextual_input["attributes"])
                self._index_entity_aliases(entity)
                resolved["entity_id"] = entity["entity_id"]
                resolved["canonical_name"] = entity["canonical_name"]
                stats["match"] += 1
            else:
                entity = self._create_entity(
                    resolved["mention"],
                    resolved["canonical_name"],
                    resolved["type"],
                    contextual_input["attributes"],
                    contextual_input["evidence"],
                    resolved["chunk_id"],
                )
                resolved["entity_id"] = entity["entity_id"]
                if decision["decision"] == "NEW_ENTITY":
                    stats["new_entity"] += 1
                else:
                    stats["unresolved"] += 1

            resolved["resolution_candidates"] = candidates
            resolved["resolution"] = {
                "method": "contextual",
                **decision,
            }

        return stats

    # --------------------------------------------------------
    # ATTRIBUTE MERGING
    # --------------------------------------------------------

    def _merge_attributes(
        self,
        entity: Dict[str, Any],
        new_attributes: Optional[Dict[str, Any]],
    ) -> None:

        if not new_attributes:
            return

        existing = entity.setdefault(
            "attributes",
            {},
        )

        for key, value in new_attributes.items():

            if key not in existing:
                existing[key] = value
                continue

            # If the existing value is a list, append new
            # values without duplication.
            if isinstance(existing[key], list):

                if isinstance(value, list):
                    for item in value:
                        if item not in existing[key]:
                            existing[key].append(item)
                else:
                    if value not in existing[key]:
                        existing[key].append(value)

                continue

            # If new value is a list but old value isn't,
            # preserve both.
            if isinstance(value, list):

                old_value = existing[key]

                if old_value not in value:
                    value = [old_value, *value]

                existing[key] = value
                continue

            # If values conflict, preserve both rather than
            # silently overwriting extracted information.
            if existing[key] != value:

                existing[key] = [
                    existing[key],
                    value,
                ]

    # --------------------------------------------------------
    # RESOLVE ALL CHUNKS
    # --------------------------------------------------------

    def resolve_extraction(
        self,
        extraction: Any,
    ) -> Dict[str, Any]:

        resolved_entities: List[Dict[str, Any]] = []

        # extraction.json in the current WSE pipeline is a
        # top-level list of chunk extraction objects.
        if isinstance(extraction, list):
            chunks = extraction

        elif isinstance(extraction, dict):
            chunks = extraction.get(
                "chunks",
                extraction.get(
                    "extractions",
                    [],
                ),
            )

        else:
            raise TypeError(
                "Unsupported extraction format: "
                f"{type(extraction).__name__}"
            )

        for chunk in chunks:
            if not isinstance(chunk, dict):
                continue

            chunk_id = chunk.get("chunk_id")
            chunk_extraction = chunk.get("extraction", chunk)

            # Failed extraction calls are recorded as `None`; they have
            # no entities to resolve and should not stop the full run.
            if not isinstance(chunk_extraction, dict):
                continue

            for extracted_entity in chunk_extraction.get("entities", []):
                if not isinstance(extracted_entity, dict):
                    continue

                resolved_entities.append(
                    self.resolve_entity(
                        extracted_entity,
                        chunk_id=chunk_id,
                    )
                )

        contextual_stats = self._resolve_contextual_mentions(
            resolved_entities
        )

        # `mentions` is the field consumed by main.py.  Keep
        # `resolved_mentions` as a compatibility alias for the standalone
        # resolver test and any earlier callers.
        return {
            "entities": self.get_entities(),
            "mentions": resolved_entities,
            "resolved_mentions": resolved_entities,
            "contextual_resolution": contextual_stats,
        }

    # --------------------------------------------------------
    # EXPORT
    # --------------------------------------------------------

    def get_entities(self) -> List[Dict[str, Any]]:
        return list(
            self.entities.values()
        )


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def resolve_entities(
    extraction: Any,
) -> Dict[str, Any]:
    """
    Main entry point.

    Example:

        result = resolve_entities(extraction)

        result["entities"]
        result["resolved_mentions"]
    """

    resolver = EntityResolver()

    return resolver.resolve_extraction(
        extraction
    )


# ============================================================
# OPTIONAL FILE-BASED TEST
# ============================================================

if __name__ == "__main__":

    import json
    from pathlib import Path

    input_path = Path(
        "output/extraction.json"
    )

    output_path = Path(
        "output/entity_resolution_test.json"
    )

    if not input_path.exists():
        print(
            f"Input file not found: {input_path}"
        )
        raise SystemExit(1)

    with input_path.open(
        "r",
        encoding="utf-8",
    ) as f:
        extraction = json.load(f)

    result = resolve_entities(
        extraction
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 60)
    print("ENTITY RESOLUTION COMPLETE")
    print("=" * 60)

    print(
        f"Canonical entities: "
        f"{len(result['entities'])}"
    )

    print(
        f"Resolved mentions: "
        f"{len(result['resolved_mentions'])}"
    )

    print(
        f"Output: {output_path}"
    )
