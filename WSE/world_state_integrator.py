def integrate_world_state(metadata, entities, mentions, contextual_resolution, extractions):
    """
    Transforms chunk-level extraction results into a global integrated world state.
    """
    
    # 1. Build Mention Lookup
    # Key: (chunk_id, mention_text)
    # Value: mention_record
    mention_lookup = {}
    for mention in mentions:
        chunk_id = mention.get("chunk_id")
        text = mention.get("mention")
        mention_lookup[(chunk_id, text)] = mention

    def resolve_reference(chunk_id, text_reference):
        """Helper to resolve a textual reference to an entity ID if possible."""
        record = mention_lookup.get((chunk_id, text_reference))
        if record:
            entity_id = record.get("entity_id")
            if entity_id:
                return {
                    "entity_id": entity_id,
                    "name": text_reference,
                    "resolution_status": "RESOLVED"
                }
        # If not found or no entity_id
        return {
            "entity_id": None,
            "name": text_reference,
            "resolution_status": "UNRESOLVED"
        }

    global_relationships = []
    global_events = []
    global_state_changes = []
    global_temporal_relations = []
    global_attributions = []

    rel_counter = 1
    event_counter = 1
    sc_counter = 1
    attr_counter = 1

    # To map local event IDs to global event IDs
    # Key: (chunk_id, local_event_id)
    # Value: global_event_id
    event_id_map = {}

    # First pass: Events (need IDs for state_changes and temporal_relations)
    for ext_record in extractions:
        chunk_id = ext_record.get("chunk_id")
        extraction = ext_record.get("extraction")
        if not extraction:
            continue

        for event in extraction.get("events", []):
            local_id = event.get("id")
            if not local_id:
                continue

            global_id = f"{chunk_id}_{local_id}"
            event_id_map[(chunk_id, local_id)] = global_id

            participants = event.get("participants", [])
            resolved_participants = [resolve_reference(chunk_id, p) for p in participants]

            location = event.get("location")
            resolved_location = resolve_reference(chunk_id, location) if location else None

            global_event = {
                "event_id": global_id,
                "source_event_id": local_id,
                "type": event.get("type"),
                "participants": resolved_participants,
                "location": resolved_location,
                "time_expression": event.get("time_expression"),
                "evidence": event.get("evidence"),
                "provenance": {
                    "chunk_id": chunk_id
                }
            }
            global_events.append(global_event)

    # Second pass: Everything else
    for ext_record in extractions:
        chunk_id = ext_record.get("chunk_id")
        extraction = ext_record.get("extraction")
        if not extraction:
            continue

        # Relationships
        for rel in extraction.get("relationships", []):
            subj = rel.get("subject")
            obj = rel.get("object")
            
            global_rel = {
                "relationship_id": f"REL_{rel_counter:04d}",
                "subject": resolve_reference(chunk_id, subj),
                "predicate": rel.get("predicate"),
                "object": resolve_reference(chunk_id, obj),
                "certainty": rel.get("certainty"),
                "evidence": rel.get("evidence"),
                "provenance": {
                    "chunk_id": chunk_id
                }
            }
            global_relationships.append(global_rel)
            rel_counter += 1

        # State Changes
        for sc in extraction.get("state_changes", []):
            entity_ref = sc.get("entity")
            caused_by = sc.get("caused_by_event")
            
            caused_by_id = None
            caused_by_text = None

            if caused_by:
                if (chunk_id, caused_by) in event_id_map:
                    caused_by_id = event_id_map[(chunk_id, caused_by)]
                else:
                    caused_by_text = caused_by

            global_sc = {
                "state_change_id": f"SC_{sc_counter:04d}",
                "entity": resolve_reference(chunk_id, entity_ref),
                "property": sc.get("property"),
                "previous_value": sc.get("previous_value"),
                "new_value": sc.get("new_value"),
                "caused_by_event_id": caused_by_id,
                "caused_by_event_text": caused_by_text,
                "evidence": sc.get("evidence"),
                "provenance": {
                    "chunk_id": chunk_id
                }
            }
            global_state_changes.append(global_sc)
            sc_counter += 1

        # Temporal Relations
        for tr in extraction.get("temporal_relations", []):
            e1 = tr.get("event_1")
            e2 = tr.get("event_2")

            global_e1 = event_id_map.get((chunk_id, e1), e1)
            global_e2 = event_id_map.get((chunk_id, e2), e2)

            global_tr = {
                "event_1": global_e1,
                "relation": tr.get("relation"),
                "event_2": global_e2,
                "evidence": tr.get("evidence"),
                "provenance": {
                    "chunk_id": chunk_id
                }
            }
            global_temporal_relations.append(global_tr)

        # Attributions
        for attr in extraction.get("attributions", []):
            source = attr.get("source")
            
            global_attr = {
                "attribution_id": f"ATTR_{attr_counter:04d}",
                "source": resolve_reference(chunk_id, source),
                "proposition": attr.get("proposition"),
                "type": attr.get("type"),
                "evidence": attr.get("evidence"),
                "provenance": {
                    "chunk_id": chunk_id
                }
            }
            global_attributions.append(global_attr)
            attr_counter += 1

    integrated_state = {
        "metadata": metadata,
        "entities": entities,
        "relationships": global_relationships,
        "events": global_events,
        "state_changes": global_state_changes,
        "temporal_relations": global_temporal_relations,
        "attributions": global_attributions,
        "resolution_summary": {
            "mentions": mentions,
            "contextual_resolution": contextual_resolution
        }
    }

    return integrated_state
