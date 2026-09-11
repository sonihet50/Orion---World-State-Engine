# Extraction Pipeline & Resolution Deep Dive

This document explains the algorithmic mechanics of the narrative information extraction pipeline.

---

## 1. Chunking Strategy (`text_splitter.py`)

Narrative fiction cannot be sliced randomly at arbitrary character counts; doing so splits dialogue quotes, sentence syntax, and entity mentions.

```
[Raw Chapter Prose (e.g. 45,000 chars)]
                    │
                    ▼
          Find "\n\n" paragraph breaks
        within (start + 0.5 * max_chars) to (start + max_chars)
                    │
                    ▼
        Chunk 1 [0 -> 7,850]    Overlap 400 chars
        Chunk 2 [7,450 -> 15,200]
        ...
```

- **Target Size**: 8,000 characters (~1,800 tokens). Fits easily within standard 8k/16k/32k LLM context windows without triggering token degradation or attention decay.
- **Overlap**: 400–500 characters. Prevents losing relationships that span across adjacent paragraphs.

---

## 2. Extraction Prompt Anatomy (`extraction_prompt.txt`)

The system prompt strictly frames the LLM as an **Information Extraction Engine**, not a creative writer.

### Key Prompt Safeguards:
1. **Direct Entailment Only**: *"Extract what the text says. Do NOT invent what the text does not say."*
2. **Persistent Relationships vs Transient Events**:
   - `Alice interviewed Bob` -> **Event**: `INTERVIEW/CONVERSATION`.
   - `Alice is married to Bob` -> **Relationship**: `MARRIED_TO`.
3. **Structured JSON Output**:
   The output structure requires:
   ```json
   {
     "entities": [{"canonical_name": "...", "mention": "...", "type": "...", "attributes": {}}],
     "relationships": [{"subject": "...", "predicate": "...", "object": "...", "certainty": "..."}],
     "events": [{"id": "...", "type": "...", "participants": [], "location": null}],
     "state_changes": [{"entity": "...", "property": "...", "previous_value": null, "new_value": "..."}],
     "temporal_relations": [{"event_1": "...", "relation": "BEFORE", "event_2": "..."}]
   }
   ```

---

## 3. Coreference Resolution & Clustering (`entity_resolution.py`)

When an LLM outputs raw mentions across multiple chunks, the same entity appears under diverse surface forms:
- Chunk 1: `"Alice"`
- Chunk 2: `"Alice Sterling"`
- Chunk 3: `"Captain Sterling"`

### Matching Heuristics:
1. **Exact & Alias Match**: Case-insensitive normalization. If `normalized(mention) == normalized(canonical)` or matches an existing alias -> **Confidence = 1.0**.
2. **Jaccard Token Similarity**:
   $$\text{sim}(A, B) = \frac{|Tokens(A) \cap Tokens(B)|}{|Tokens(A) \cup Tokens(B)|}$$
3. **Substring Containment**:
   If `"Alice"` is a strict substring of `"Alice Sterling"`, score is $\frac{\text{len}(A)}{\text{len}(B)}$.
4. **Clustering Threshold**:
   Pairs scoring $\ge 0.85$ are merged into a single canonical entity cluster, preserving all surface forms as `EntityAlias` records.

---

## 4. Rule-Based Contradiction Detection (SRS REQ-27)

Contradictions are detected strictly via code algorithms in [`ConsistencyService`](../../app/services/consistency_service.py):

### Rule 1: Age Monotonicity (REQ-23)
- If `property_name == "age"`:
  - Parse numerical integers.
  - If chapter index $B > A$ and $\text{age}(B) < \text{age}(A)$, flag as `FACT_FACT` contradiction.

### Rule 2: Post-Mortem Action (REQ-26)
- Maintain a set of characters with status `DEAD` (or affected by a `DEATH` event).
- If a deceased character appears as an active speaker or participant in a subsequent chapter event, flag as `EVENT_LOCATION` / status contradiction.

### Rule 3: Mutually Exclusive Relationships (REQ-25)
- Look up incompatible pairs (e.g. `ENEMY_OF` and `MARRIED_TO`, or `FATHER_OF` changing to a different entity).
- Flag as `RELATIONSHIP_RELATIONSHIP` contradiction.

### Rule 4: Temporal Ordering Cycles via DFS (REQ-27)
- Build a directed graph from `temporal_relations` (`BEFORE` $\to$ directed edge $A \to B$; `AFTER` $\to B \to A$).
- Run Depth-First Search with 3-color node states (0: unvisited, 1: visiting, 2: visited).
- If a node is visited while in state 1, a directed cycle exists. Backtrack the path and flag as a `CYCLE` contradiction.
