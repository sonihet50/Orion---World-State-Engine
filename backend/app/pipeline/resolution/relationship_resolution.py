from typing import Dict, Any, Optional, Tuple
from app.core.constants import RelationshipStatus, ContradictionType

INCOMPATIBLE_RELATIONSHIP_PAIRS = {
    ("ENEMY_OF", "FRIEND_OF"),
    ("ENEMY_OF", "MARRIED_TO"),
    ("DEAD_AT_HANDS_OF", "ALLY_OF")
}

def resolve_relationship_update(
    old_type: str,
    new_type: str,
    subj_name: str,
    obj_name: str
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Evaluates relationship type updates.
    Returns: (status, optional_contradiction_info)
    """
    if not old_type:
        return RelationshipStatus.ACTIVE.value, None

    old_norm = old_type.strip().upper()
    new_norm = new_type.strip().upper()

    if old_norm == new_norm:
        return RelationshipStatus.ACTIVE.value, None

    # Check for direct incompatibility
    pair = (old_norm, new_norm)
    reverse_pair = (new_norm, old_norm)

    is_direct_conflict = (pair in INCOMPATIBLE_RELATIONSHIP_PAIRS or reverse_pair in INCOMPATIBLE_RELATIONSHIP_PAIRS)

    if is_direct_conflict:
        status = RelationshipStatus.CONTRADICTED.value
        explanation = (
            f"Relationship conflict between '{subj_name}' and '{obj_name}': "
            f"previous relationship '{old_type}' is fundamentally incompatible with new '{new_type}'."
        )
    else:
        status = RelationshipStatus.SUPERSEDED.value
        explanation = (
            f"Relationship evolution between '{subj_name}' and '{obj_name}': "
            f"type updated from '{old_type}' to '{new_type}'."
        )

    contradiction_info = {
        "contradiction_type": ContradictionType.RELATIONSHIP_RELATIONSHIP.value,
        "old_type": old_type,
        "new_type": new_type,
        "explanation": explanation
    }

    return status, contradiction_info
