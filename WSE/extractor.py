import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/chat"

MODEL_NAME = "llama3.1:8b-instruct-q4_K_M"

REQUEST_TIMEOUT_SECONDS = 600


def post_ollama(payload, request_label="Ollama request"):
    """Send one JSON request to the local Ollama API without extra packages."""

    payload_bytes = len(json.dumps(payload).encode("utf-8"))
    started_at = time.perf_counter()

    print(
        f"[{request_label}] Sending {payload_bytes:,} bytes "
        f"(timeout: {REQUEST_TIMEOUT_SECONDS}s)...",
        flush=True,
    )

    request = Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError) as error:
        elapsed = time.perf_counter() - started_at
        print(
            f"[{request_label}] Failed after {elapsed:.1f}s: {error}",
            flush=True,
        )
        raise RuntimeError(f"Ollama request failed: {error}") from error

    elapsed = time.perf_counter() - started_at
    print(
        f"[{request_label}] Completed in {elapsed:.1f}s; "
        f"prompt_eval={result.get('prompt_eval_count')}, "
        f"eval={result.get('eval_count')}, "
        f"done_reason={result.get('done_reason')}.",
        flush=True,
    )

    return result


# ============================================================
# STRICT JSON SCHEMA
# ============================================================

EXTRACTION_JSON_SCHEMA = {
    "type": "object",

    "properties": {

        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {

                    "mention": {
                        "type": "string"
                    },

                    "canonical_name": {
                        "type": "string"
                    },

                    "type": {
                        "type": "string"
                    },

                    "attributes": {
                        "type": "object"
                    },

                    "evidence": {
                        "type": "string"
                    }
                },

                "required": [
                    "mention",
                    "canonical_name",
                    "type",
                    "attributes",
                    "evidence"
                ]
            }
        },

        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {

                    "subject": {
                        "type": "string"
                    },

                    "predicate": {
                        "type": "string"
                    },

                    "object": {
                        "type": "string"
                    },

                    "certainty": {
                        "type": "string"
                    },

                    "evidence": {
                        "type": "string"
                    }
                },

                "required": [
                    "subject",
                    "predicate",
                    "object",
                    "certainty",
                    "evidence"
                ]
            }
        },

        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {

                    "id": {
                        "type": "string"
                    },

                    "type": {
                        "type": "string"
                    },

                    "participants": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },

                    "location": {
                        "type": [
                            "string",
                            "null"
                        ]
                    },

                    "time_expression": {
                        "type": [
                            "string",
                            "null"
                        ]
                    },

                    "evidence": {
                        "type": "string"
                    }
                },

                "required": [
                    "id",
                    "type",
                    "participants",
                    "location",
                    "time_expression",
                    "evidence"
                ]
            }
        },

        "state_changes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {

                    "entity": {
                        "type": "string"
                    },

                    "property": {
                        "type": "string"
                    },

                    "previous_value": {
                        "type": [
                            "string",
                            "null"
                        ]
                    },

                    "new_value": {
                        "type": "string"
                    },

                    "caused_by_event": {
                        "type": [
                            "string",
                            "null"
                        ]
                    },

                    "evidence": {
                        "type": "string"
                    }
                },

                "required": [
                    "entity",
                    "property",
                    "previous_value",
                    "new_value",
                    "caused_by_event",
                    "evidence"
                ]
            }
        },

        "temporal_relations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {

                    "event_1": {
                        "type": "string"
                    },

                    "relation": {
                        "type": "string"
                    },

                    "event_2": {
                        "type": "string"
                    },

                    "evidence": {
                        "type": "string"
                    }
                },

                "required": [
                    "event_1",
                    "relation",
                    "event_2",
                    "evidence"
                ]
            }
        },

        "attributions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {

                    "source": {
                        "type": "string"
                    },

                    "proposition": {
                        "type": "string"
                    },

                    "type": {
                        "type": "string"
                    },

                    "evidence": {
                        "type": "string"
                    }
                },

                "required": [
                    "source",
                    "proposition",
                    "type",
                    "evidence"
                ]
            }
        }
    },

    "required": [
        "entities",
        "relationships",
        "events",
        "state_changes",
        "temporal_relations",
        "attributions"
    ]
}


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the World State Extraction module of the
World State Engine.

You extract structured information from narrative text.

You are NOT a creative writing assistant.

Only extract information supported by the supplied text.

Do not invent facts, attributes, relationships,
events, locations, nationalities, occupations,
or other information.

Every extraction must be grounded in the narrative.

IMPORTANT:

The response MUST follow the supplied JSON schema exactly.

For entities:

mention:
    The exact name or referring expression appearing
    in the text.

canonical_name:
    The best-supported name for that entity based ONLY
    on the text.

type:
    CHARACTER, LOCATION, ORGANIZATION, OBJECT, OTHER

Do not invent a canonical name.

For example:

If the text says:

"Rob walked into the room."

Return:

mention = "Rob"
canonical_name = "Rob"

Do NOT invent:

canonical_name = "Robert Guthard"

unless the text actually supports that.

For relationships:

Only extract persistent or meaningful relationships.

For actions such as:

"Alice interviewed Rob."

prefer an EVENT rather than a persistent relationship.

For events:

Extract things that actually happen.

Use specific event types such as:

TRAVEL
DEPARTURE
ARRIVAL
MEETING
CONVERSATION
DISCOVERY
INVESTIGATION
CONFLICT
ATTACK
DEATH
COMMUNICATION
EMPLOYMENT
LOCATION_CHANGE
OTHER

For state changes:

Only create a state change when the text explicitly
states or strongly supports a change.

Do not infer nationality from location.

Do not infer occupation from an event.

Do not infer relationships merely from proximity.

For beliefs:

Keep subjective statements separate from objective facts.

For example:

"Rob believed the woman was dangerous."

should be represented as an attribution rather than
as the objective fact that the woman was dangerous.

Evidence must come from the supplied narrative.

If a category contains no information, return [].

Return ONLY JSON.
"""


# ============================================================
# EXTRACTION FUNCTION
# ============================================================

def extract_from_chunk(chunk, chunk_id):

    user_prompt = f"""
Extract world-state information from this manuscript chunk.

CHUNK ID:
{chunk_id}

TEXT:
--------------------------------------------------
{chunk}
--------------------------------------------------

Remember:

- Extract only supported information.
- Do not guess.
- Do not invent canonical names.
- Do not invent attributes.
- Distinguish events from persistent relationships.
- Only create state changes when supported.
- Preserve uncertainty.
- Include evidence.
- Return all required top-level fields.
- Return [] for empty categories.
"""

    payload = {

        "model": MODEL_NAME,

        "messages": [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": user_prompt
            }
        ],

        "stream": False,

        # IMPORTANT:
        # Give Ollama the actual JSON schema instead
        # of simply saying "return JSON".
        "format": EXTRACTION_JSON_SCHEMA,

        "options": {
            "temperature": 0
        }
    }

    # --------------------------------------------------------
    # CALL OLLAMA
    # --------------------------------------------------------

    schema_chars = len(json.dumps(EXTRACTION_JSON_SCHEMA))
    estimated_input_tokens = (
        len(SYSTEM_PROMPT) + len(user_prompt) + schema_chars
    ) // 4

    print(
        f"[{chunk_id}] chunk_chars={len(chunk):,}; "
        f"system_chars={len(SYSTEM_PROMPT):,}; "
        f"user_prompt_chars={len(user_prompt):,}; "
        f"schema_chars={schema_chars:,}; "
        f"estimated_input_tokens_about={estimated_input_tokens:,}.",
        flush=True,
    )

    result = post_ollama(
        payload,
        request_label=f"{chunk_id} extraction",
    )

    # --------------------------------------------------------
    # GET MODEL CONTENT
    # --------------------------------------------------------

    if "message" not in result:

        return {
            "_error": "Ollama response missing message",
            "_raw_response": result
        }

    content = result["message"].get(
        "content",
        ""
    )

    # --------------------------------------------------------
    # PARSE JSON
    # --------------------------------------------------------

    try:

        data = json.loads(content)

    except json.JSONDecodeError:

        return {
            "_error": "Model returned invalid JSON",
            "_raw_response": content
        }

    # --------------------------------------------------------
    # NORMALIZE
    # --------------------------------------------------------

    collection_fields = [
        "entities",
        "relationships",
        "events",
        "state_changes",
        "temporal_relations",
        "attributions"
    ]

    for field in collection_fields:

        if field not in data:
            data[field] = []

        elif data[field] is None:
            data[field] = []

    return data
