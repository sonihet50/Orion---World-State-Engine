def check_consistency(world_state):
    """
    Performs basic structural consistency checks on the integrated world state.
    """
    issues = []
    issue_counter = 1

    def add_issue(type_, severity, description, provenance):
        nonlocal issue_counter
        issues.append({
            "issue_id": f"ISSUE_{issue_counter:04d}",
            "type": type_,
            "severity": severity,
            "description": description,
            "provenance": provenance
        })
        issue_counter += 1

    # 1. Valid Entity References
    valid_entity_ids = {e.get("entity_id") for e in world_state.get("entities", []) if e.get("entity_id")}
    
    def check_entity_ref(ref_obj, context, provenance):
        if not ref_obj:
            return
        if ref_obj.get("resolution_status") == "RESOLVED":
            eid = ref_obj.get("entity_id")
            if eid not in valid_entity_ids:
                add_issue(
                    "INVALID_ENTITY_REFERENCE",
                    "ERROR",
                    f"Resolved reference to unknown entity ID: {eid} in {context}",
                    provenance
                )

    # 2. Duplicate Global IDs
    seen_ids = set()
    def check_id_uniqueness(item_id, context, provenance):
        if item_id in seen_ids:
            add_issue(
                "DUPLICATE_GLOBAL_ID",
                "ERROR",
                f"Duplicate global ID found: {item_id} in {context}",
                provenance
            )
        else:
            seen_ids.add(item_id)

    # Validate Relationships
    for rel in world_state.get("relationships", []):
        prov = rel.get("provenance", {})
        rel_id = rel.get("relationship_id")
        check_id_uniqueness(rel_id, "relationships", prov)
        check_entity_ref(rel.get("subject"), f"relationship {rel_id} subject", prov)
        check_entity_ref(rel.get("object"), f"relationship {rel_id} object", prov)

    # Valid Event References setup
    valid_event_ids = set()
    for event in world_state.get("events", []):
        prov = event.get("provenance", {})
        event_id = event.get("event_id")
        check_id_uniqueness(event_id, "events", prov)
        valid_event_ids.add(event_id)
        
        for i, p in enumerate(event.get("participants", [])):
            check_entity_ref(p, f"event {event_id} participant {i}", prov)
        
        check_entity_ref(event.get("location"), f"event {event_id} location", prov)

    # Validate State Changes
    for sc in world_state.get("state_changes", []):
        prov = sc.get("provenance", {})
        sc_id = sc.get("state_change_id")
        check_id_uniqueness(sc_id, "state_changes", prov)
        
        check_entity_ref(sc.get("entity"), f"state change {sc_id} entity", prov)
        
        caused_by = sc.get("caused_by_event_id")
        if caused_by and caused_by not in valid_event_ids:
            add_issue(
                "INVALID_EVENT_REFERENCE",
                "ERROR",
                f"State change {sc_id} references unknown event ID: {caused_by}",
                prov
            )

    # Validate Attributions
    for attr in world_state.get("attributions", []):
        prov = attr.get("provenance", {})
        attr_id = attr.get("attribution_id")
        check_id_uniqueness(attr_id, "attributions", prov)
        check_entity_ref(attr.get("source"), f"attribution {attr_id} source", prov)

    # Validate Temporal Relations & Build Graph for Cycle Detection
    graph = {eid: [] for eid in valid_event_ids}
    
    for tr in world_state.get("temporal_relations", []):
        prov = tr.get("provenance", {})
        e1 = tr.get("event_1")
        e2 = tr.get("event_2")
        rel_type = tr.get("relation", "").upper()
        
        if e1 not in valid_event_ids:
            add_issue("INVALID_EVENT_REFERENCE", "ERROR", f"Temporal relation references unknown event 1: {e1}", prov)
        if e2 not in valid_event_ids:
            add_issue("INVALID_EVENT_REFERENCE", "ERROR", f"Temporal relation references unknown event 2: {e2}", prov)

        if e1 in valid_event_ids and e2 in valid_event_ids:
            if rel_type == "BEFORE":
                graph[e1].append(e2)
            elif rel_type == "AFTER":
                graph[e2].append(e1)

    # Cycle Detection using DFS
    visited = {} # node -> 0: unvisited, 1: visiting, 2: visited
    for node in graph:
        visited[node] = 0

    def dfs(node, path):
        visited[node] = 1
        path.append(node)
        for neighbor in graph.get(node, []):
            if visited.get(neighbor) == 0:
                if dfs(neighbor, path):
                    return True
            elif visited.get(neighbor) == 1:
                # Cycle found
                cycle_start_idx = path.index(neighbor)
                cycle = path[cycle_start_idx:] + [neighbor]
                add_issue(
                    "TEMPORAL_CYCLE",
                    "ERROR",
                    f"Temporal cycle detected: {' -> '.join(cycle)}",
                    {"cycle": cycle}
                )
                return True
        path.pop()
        visited[node] = 2
        return False

    for node in graph:
        if visited[node] == 0:
            dfs(node, [])

    summary = {
        "status": "completed",
        "issues_found": len(issues)
    }

    return {
        "summary": summary,
        "issues": issues
    }
