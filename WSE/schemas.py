EXTRACTION_SCHEMA = {
    "entities": [
        {
            "mention": "exact mention from text",
            "canonical_name": "best-supported name",
            "type": "CHARACTER | LOCATION | ORGANIZATION | OBJECT | OTHER",
            "attributes": {},
            "evidence": "short supporting text"
        }
    ],

    "relationships": [
        {
            "subject": "entity mention",
            "predicate": "relationship",
            "object": "entity mention",
            "certainty": "ASSERTED | UNCERTAIN | BELIEF | RUMOR",
            "evidence": "short supporting text"
        }
    ],

    "events": [
        {
            "id": "E001",
            "type": "TRAVEL | DEPARTURE | ARRIVAL | MEETING | "
                   "CONVERSATION | DISCOVERY | INVESTIGATION | "
                   "CONFLICT | ATTACK | DEATH | COMMUNICATION | "
                   "EMPLOYMENT | LOCATION_CHANGE | OTHER",
            "participants": [],
            "location": None,
            "time_expression": None,
            "evidence": "short supporting text"
        }
    ],

    "state_changes": [
        {
            "entity": "entity mention",
            "property": "property that changed",
            "previous_value": None,
            "new_value": "new value",
            "caused_by_event": None,
            "evidence": "explicit evidence of the change"
        }
    ],

    "temporal_relations": [
        {
            "event_1": "E001",
            "relation": "BEFORE | AFTER | DURING | SIMULTANEOUS",
            "event_2": "E002",
            "evidence": "supporting text"
        }
    ],

    "attributions": [
        {
            "source": "entity",
            "proposition": "what the source believes/knows/etc.",
            "type": "BELIEF | KNOWLEDGE | RUMOR | DENIAL | SUSPICION",
            "evidence": "supporting text"
        }
    ]
}