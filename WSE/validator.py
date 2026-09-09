REQUIRED_FIELDS = [
    "entities",
    "relationships",
    "events",
    "state_changes",
    "temporal_relations",
    "attributions"
]


def validate_extraction(data):

    errors = []

    if not isinstance(data, dict):
        return ["Extraction is not a JSON object."]

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(
                f"Missing required field: {field}"
            )

    if errors:
        return errors

    # Validate entities
    for i, entity in enumerate(data["entities"]):

        required = [
            "mention",
            "canonical_name",
            "type"
        ]

        for field in required:
            if field not in entity:
                errors.append(
                    f"Entity {i} missing '{field}'"
                )

    # Validate relationships
    for i, relation in enumerate(data["relationships"]):

        required = [
            "subject",
            "predicate",
            "object",
            "certainty",
            "evidence"
        ]

        for field in required:
            if field not in relation:
                errors.append(
                    f"Relationship {i} missing '{field}'"
                )

    # Validate events
    for i, event in enumerate(data["events"]):

        required = [
            "id",
            "type",
            "participants",
            "evidence"
        ]

        for field in required:
            if field not in event:
                errors.append(
                    f"Event {i} missing '{field}'"
                )

    return errors