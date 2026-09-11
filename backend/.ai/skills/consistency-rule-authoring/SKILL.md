---
name: consistency-rule-authoring
description: Recipe for implementing deterministic, rule-based contradiction checks per SRS REQ-23..28.
---

# Skill: Authoring Consistency & Contradiction Rules

Per **SRS REQ-27**, all contradiction detection must be **rule-based and shall not rely on a language model**. Follow this guide when adding or refining consistency rules.

---

## 1. Rule Architecture in `ConsistencyService`

All rules reside in [`app/services/consistency_service.py`](../../app/services/consistency_service.py).
Every rule follows the standard contract:
- **Input**: Extracted entities, facts, relationships, or events.
- **Computation**: Pure Python deterministic verification (hashing, graph search, mathematical comparison).
- **Output**: List of [`Contradiction`](../../app/models/contradiction.py) records with `contradiction_type`, `explanation`, `confidence`, and associated version/event FKs.

---

## 2. Implementing the 4 Core SRS Rule Types

### Rule 1: Age Monotonicity (SRS REQ-23)
Detects when a character's chronological age decreases across subsequent chapters:
```python
def check_age_monotonicity(entity_id: str, fact_history: List[FactVersion]):
    sorted_versions = sorted(fact_history, key=lambda v: v.chapter.chapter_number)
    for i in range(1, len(sorted_versions)):
        prev_age = int(sorted_versions[i-1].value)
        curr_age = int(sorted_versions[i].value)
        if curr_age < prev_age:
            return {
                "type": "FACT_FACT",
                "explanation": f"Age decreased from {prev_age} (Ch. {sorted_versions[i-1].chapter.chapter_number}) to {curr_age} (Ch. {sorted_versions[i].chapter.chapter_number}) without flashback marker."
            }
```

### Rule 2: Location Clashes (SRS REQ-24)
Detects a character participating in events in two geographically distant locations during the same chapter or simultaneous timeframe.

### Rule 3: Relationship Incompatibilities (SRS REQ-25)
Detects logically irreconcilable relationship mutations:
```python
INCOMPATIBLE_PAIRS = {
    ("ENEMY_OF", "MARRIED_TO"),
    ("ALLY_OF", "NEMESIS_OF")
}
```

### Rule 4: Post-Mortem Actions (SRS REQ-26)
Checks whether an entity marked `status: DEAD` or subject to a prior `DEATH` event participates in speech or actions in a subsequent chapter.

### Rule 5: Temporal Graph Cycles (SRS REQ-27)
Builds an adjacency list of events from `BEFORE`/`AFTER` relations and executes Depth-First Search cycle detection. If a back-edge is visited, a temporal paradox exists.

---

## Verification

Add a unit test in [`app/tests/test_services.py`](../../app/tests/test_services.py) proving the rule detects the contradiction and returns 0 false-positives:
```bash
PYTHONPATH=backend pytest app/tests/test_services.py -k "test_consistency" -v
```
