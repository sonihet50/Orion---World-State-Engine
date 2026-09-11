# REST API Contracts & Endpoint Specifications

All endpoints are mounted with the prefix `/api/v1` and mirrored at the root (`/worlds`, `/jobs`, etc.) for seamless frontend compatibility.

---

## 1. Authentication (`/api/v1/auth`)

### `POST /auth/register`
- **Request**: `{ "email": "author@example.com", "password": "securepassword" }`
- **Response** (`201 Created`):
  ```json
  {
    "id": "uuid-string",
    "email": "author@example.com",
    "created_at": "2026-09-10T12:00:00Z",
    "updated_at": "2026-09-10T12:00:00Z"
  }
  ```

### `POST /auth/login`
- **Request**: `{ "email": "author@example.com", "password": "securepassword" }`
- **Response** (`200 OK`):
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer"
  }
  ```

### `GET /auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response** (`200 OK`): Current user object.

---

## 2. Worlds / Projects (`/api/v1/worlds`)

### `POST /worlds`
- **Request**: `{ "name": "Terra Incognita", "description": "High-fantasy setting" }`
- **Response** (`201 Created`): World object with initial stats (`entities_count: 0`, etc.).

### `GET /worlds`
- **Query Params**: `user_id` (optional, auto-inferred from auth token).
- **Response** (`200 OK`): Array of World objects with aggregated statistics:
  ```json
  [
    {
      "id": "terra-incognita",
      "name": "Terra Incognita",
      "description": "High-fantasy setting",
      "created_at": "2026-09-10T12:00:00Z",
      "stats": {
        "entities_count": 42,
        "characters_count": 18,
        "locations_count": 12,
        "objects_count": 8,
        "relationships_count": 35,
        "events_count": 24,
        "contradictions_count": 3
      }
    }
  ]
  ```

---

## 3. Manuscripts & Chapters

### `POST /worlds/{world_id}/manuscripts`
- **Content-Type**: `multipart/form-data`
- **Body**: `file`: uploaded binary (`.txt`, `.docx`, `.pdf`).
- **Response** (`202 Accepted`):
  ```json
  {
    "job_id": "job-uuid-123",
    "manuscript_id": "ms-uuid-456",
    "chapters_total": 12,
    "message": "Manuscript accepted for processing"
  }
  ```

### `PUT /worlds/{world_id}/chapters/{chapter_id}`
- **Request**: `{ "title": "Chapter 2: The Return", "content": "Full revised narrative prose..." }`
- **Response** (`202 Accepted`):
  ```json
  {
    "chapter_id": "ch-uuid",
    "version_id": "ver-uuid-2",
    "job_id": "job-uuid-789",
    "status": "re_extraction_queued"
  }
  ```

---

## 4. Processing Jobs (Polling)

### `GET /jobs/{job_id}/status`
- **Response** (`200 OK`):
  ```json
  {
    "id": "job-uuid-123",
    "status": "processing",  // "queued" | "processing" | "done" | "failed"
    "progress_current": 4,
    "progress_total": 12,
    "error_message": null
  }
  ```

---

## 5. Entities & Knowledge Graph

### `GET /worlds/{world_id}/entities`
- **Query Params**: `entity_type` (optional: `character`, `location`, `object`).
- **Response** (`200 OK`): Array of entities with active facts and aliases.

### `GET /worlds/{world_id}/graph`
- **Response** (`200 OK`):
  ```json
  {
    "nodes": [
      {
        "id": "ent-1",
        "label": "Alice Sterling",
        "type": "character",
        "degree": 4,
        "properties": { "rank": "Captain", "status": "active" }
      }
    ],
    "edges": [
      {
        "id": "rel-1",
        "source": "ent-1",
        "target": "ent-2",
        "type": "FRIEND_OF",
        "confidence": 1.0,
        "status": "ACTIVE"
      }
    ]
  }
  ```

---

## 6. Timeline & Comparisons

### `GET /worlds/{world_id}/timeline`
- **Response** (`200 OK`): Ordered chronological events with participant roles and chapter tags.

### `GET /worlds/{world_id}/timeline/compare?chapter_a=1&chapter_b=5`
- **Response** (`200 OK`):
  ```json
  {
    "chapter_a": 1,
    "chapter_b": 5,
    "new_entities": ["Bob"],
    "state_changes": [
      { "entity": "Alice", "property": "location", "from": "London", "to": "Paris" }
    ],
    "contradictions": []
  }
  ```

---

## 7. Contradiction Management

### `GET /worlds/{world_id}/contradictions`
- **Query Params**: `status` (optional: `DETECTED`, `RESOLVED`, `DISMISSED`).
- **Response** (`200 OK`): List of contradictions with conflict explanations and version IDs.

### `POST /worlds/{world_id}/contradictions/{con_id}/resolve`
- **Request**:
  ```json
  {
    "status": "RESOLVED",
    "preferred_fact_version_id": "fact-ver-uuid-2",
    "resolution_notes": "Author confirmed Alice has brown eyes, not blue."
  }
  ```
- **Response** (`200 OK`): Updated Contradiction object.

---

## 8. Grounded Character Chat

### `POST /worlds/{world_id}/chat`
- **Request**:
  ```json
  {
    "message": "Where were you during the siege of Camelot?",
    "entity_focus": "King Arthur",
    "history": []
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "response": "According to the manuscript chronicles, I was stationed at the Northern Gate commanding the vanguard.",
    "citations": [
      {
        "source_type": "event",
        "source_id": "ev-102",
        "title": "Siege of Camelot",
        "snippet": "Arthur took position by the northern ramparts..."
      }
    ],
    "suggested_actions": ["Inspect King Arthur's location history"]
  }
  ```
