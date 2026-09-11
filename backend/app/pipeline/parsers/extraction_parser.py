import json
import re
from typing import Dict, Any, List, Tuple

def clean_json_response(raw_text: str) -> str:
    """Removes markdown code fences and cleans up raw LLM responses."""
    text = raw_text.strip()
    
    # Remove markdown code block fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    # Sometimes LLM outputs leading text before {
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]

    # Clean trailing commas in arrays/objects: ,] or ,}
    text = re.sub(r',\s*([\]}])', r'\1', text)

    return text


def parse_and_validate_extraction(raw_text: str) -> Tuple[Dict[str, Any], List[str]]:
    """
    Parses LLM output and validates basic schema structure.
    Returns: (sanitized_extraction_dict, list_of_errors)
    """
    errors = []
    cleaned = clean_json_response(raw_text)

    try:
        data = json.loads(cleaned)
    except Exception as e:
        return {
            "entities": [],
            "relationships": [],
            "events": [],
            "state_changes": [],
            "temporal_relations": []
        }, [f"JSON Parse Error: {str(e)}"]

    if not isinstance(data, dict):
        return {
            "entities": [],
            "relationships": [],
            "events": [],
            "state_changes": [],
            "temporal_relations": []
        }, ["Extraction output is not a JSON object"]

    result: Dict[str, Any] = {
        "entities": [],
        "relationships": [],
        "events": [],
        "state_changes": [],
        "temporal_relations": []
    }

    # 1. Sanitize Entities
    raw_entities = data.get("entities", [])
    if isinstance(raw_entities, list):
        for idx, item in enumerate(raw_entities):
            if isinstance(item, dict):
                canonical = str(item.get("canonical_name") or item.get("name") or item.get("mention") or "").strip()
                if not canonical:
                    continue
                mention = str(item.get("mention") or canonical).strip()
                ent_type = str(item.get("type") or "unknown").strip().lower()
                attrs = item.get("attributes", {})
                if not isinstance(attrs, dict):
                    attrs = {}
                evidence = str(item.get("evidence") or "").strip()

                result["entities"].append({
                    "mention": mention,
                    "canonical_name": canonical,
                    "type": ent_type,
                    "attributes": attrs,
                    "evidence": evidence
                })

    # 2. Sanitize Relationships
    raw_rels = data.get("relationships", [])
    if isinstance(raw_rels, list):
        for item in raw_rels:
            if isinstance(item, dict):
                subject = str(item.get("subject") or "").strip()
                predicate = str(item.get("predicate") or "RELATED_TO").strip().upper()
                obj = str(item.get("object") or "").strip()
                certainty = str(item.get("certainty") or "DEFINITE").strip().upper()
                evidence = str(item.get("evidence") or "").strip()

                if subject and obj:
                    result["relationships"].append({
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "certainty": certainty,
                        "evidence": evidence
                    })

    # 3. Sanitize Events
    raw_events = data.get("events", [])
    if isinstance(raw_events, list):
        for idx, item in enumerate(raw_events):
            if isinstance(item, dict):
                ev_id = str(item.get("id") or f"event_{idx + 1}").strip()
                ev_type = str(item.get("type") or "EVENT").strip().upper()
                participants = item.get("participants", [])
                if isinstance(participants, str):
                    participants = [participants]
                elif not isinstance(participants, list):
                    participants = []
                participants = [str(p).strip() for p in participants if str(p).strip()]

                location = item.get("location")
                if location is not None:
                    location = str(location).strip()

                time_expr = item.get("time_expression")
                if time_expr is not None:
                    time_expr = str(time_expr).strip()

                evidence = str(item.get("evidence") or "").strip()

                result["events"].append({
                    "id": ev_id,
                    "type": ev_type,
                    "participants": participants,
                    "location": location,
                    "time_expression": time_expr,
                    "evidence": evidence
                })

    # 4. State Changes
    raw_sc = data.get("state_changes", [])
    if isinstance(raw_sc, list):
        for item in raw_sc:
            if isinstance(item, dict):
                entity = str(item.get("entity") or "").strip()
                prop = str(item.get("property") or "").strip()
                new_val = item.get("new_value")
                if entity and prop and new_val is not None:
                    result["state_changes"].append({
                        "entity": entity,
                        "property": prop,
                        "previous_value": item.get("previous_value"),
                        "new_value": new_val,
                        "caused_by_event": item.get("caused_by_event"),
                        "evidence": str(item.get("evidence") or "").strip()
                    })

    # 5. Temporal Relations
    raw_tr = data.get("temporal_relations", [])
    if isinstance(raw_tr, list):
        for item in raw_tr:
            if isinstance(item, dict):
                e1 = str(item.get("event_1") or "").strip()
                rel = str(item.get("relation") or "BEFORE").strip().upper()
                e2 = str(item.get("event_2") or "").strip()
                if e1 and e2:
                    result["temporal_relations"].append({
                        "event_1": e1,
                        "relation": rel,
                        "event_2": e2,
                        "evidence": str(item.get("evidence") or "").strip()
                    })

    return result, errors
