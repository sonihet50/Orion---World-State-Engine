import json
from world_state_integrator import integrate_world_state
from consistency_checker import check_consistency
from entity_resolver import resolve_entities

with open("output/extraction.json", "r", encoding="utf-8") as f:
    all_extractions = json.load(f)

# Mock metadata
metadata = {
    "source_file": "test",
    "num_chunks": len(all_extractions),
    "pipeline": ["world_state_integration"]
}

print("Running entity resolution...")
resolution = resolve_entities(all_extractions)

print("Running integration...")
world_state = integrate_world_state(
    metadata=metadata,
    entities=resolution.get("entities", []),
    mentions=resolution.get("mentions", []),
    contextual_resolution=resolution.get("contextual_resolution", {}),
    extractions=all_extractions
)

print(f"Entities:              {len(world_state.get('entities', []))}")
print(f"Relationships:         {len(world_state.get('relationships', []))}")
print(f"Events:                {len(world_state.get('events', []))}")
print(f"State changes:         {len(world_state.get('state_changes', []))}")
print(f"Temporal relations:    {len(world_state.get('temporal_relations', []))}")
print(f"Attributions:          {len(world_state.get('attributions', []))}")

print("Running consistency check...")
consistency_results = check_consistency(world_state)
print(f"Issues found: {consistency_results['summary']['issues_found']}")
for issue in consistency_results.get("issues", []):
    print(f"  - [{issue['severity']}] {issue['type']}: {issue['description']}")

with open("output/world_state_test.json", "w") as f:
    json.dump(world_state, f, indent=2)

print("Done. Saved to output/world_state_test.json")
