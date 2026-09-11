from typing import Any, Dict, Optional, Tuple
from app.core.constants import FactStatus, ContradictionType

def compare_fact_values(old_val: Any, new_val: Any) -> bool:
    """Returns True if values represent the same information."""
    if old_val == new_val:
        return True
    if str(old_val).strip().lower() == str(new_val).strip().lower():
        return True
    return False


def resolve_fact_update(
    property_name: str,
    old_value: Any,
    new_value: Any,
    entity_name: str = "Entity"
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Evaluates an attribute update against an existing active value.
    Returns: (new_status, optional_contradiction_info)
    """
    if old_value is None or old_value == "":
        return FactStatus.ACTIVE.value, None

    if compare_fact_values(old_value, new_value):
        # Unchanged
        return FactStatus.ACTIVE.value, None

    # Values conflict:
    # Check if this is a mutable property (e.g. location, title) vs immutable (e.g. eye color, birth place)
    immutable_props = {"birth_place", "date_of_birth", "origin", "eye_color", "species"}
    
    if property_name.lower() in immutable_props:
        status = FactStatus.CONTRADICTED.value
        explanation = (
            f"Direct contradiction for '{entity_name}': property '{property_name}' "
            f"was previously stated as '{old_value}' but is now stated as '{new_value}'."
        )
    else:
        status = FactStatus.SUPERSEDED.value
        explanation = (
            f"State transition or conflict for '{entity_name}': property '{property_name}' "
            f"updated from '{old_value}' to '{new_value}'."
        )

    contradiction_info = {
        "contradiction_type": ContradictionType.FACT_FACT.value,
        "property_name": property_name,
        "old_value": old_value,
        "new_value": new_value,
        "explanation": explanation
    }

    return status, contradiction_info
