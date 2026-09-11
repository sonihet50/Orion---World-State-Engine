# Database Schema Reference (ER Diagram v2)

This document provides the definitive schema reference for all 12 relational database tables in the Orion backend, matching `wse_er_diagram_v2.puml`.

---

## 1. Core Tables

### `users`
- **`id`** (`VARCHAR(36)`, PK): UUID string.
- **`email`** (`VARCHAR(255)`, UNIQUE, INDEX): Account email address.
- **`password_hash`** (`VARCHAR(255)`): Bcrypt hash with salt rounds.
- **`created_at`** (`TIMESTAMP`): Creation timestamp.
- **`updated_at`** (`TIMESTAMP`): Last modification timestamp.

### `worlds`
- **`id`** (`VARCHAR(36)`, PK): UUID string.
- **`user_id`** (`VARCHAR(36)`, FK -> `users.id`, `ON DELETE SET NULL`): Owner user.
- **`name`** (`VARCHAR(255)`): Project/World title.
- **`description`** (`TEXT`): World premise or simulation description.
- **`created_at`** (`TIMESTAMP`), **`updated_at`** (`TIMESTAMP`).

---

## 2. Manuscript & Chapter Tables

### `manuscripts`
- **`id`** (`VARCHAR(36)`, PK): UUID string.
- **`world_id`** (`VARCHAR(36)`, FK -> `worlds.id`, `ON DELETE CASCADE`): Parent world.
- **`title`** (`VARCHAR(255)`): Original uploaded filename or manuscript title.
- **`original_file_path`** (`TEXT`): Path in storage volume.
- **`file_type`** (`VARCHAR(50)`): MIME type (e.g. `text/plain`, `.docx`, `.pdf`).
- **`created_at`** (`TIMESTAMP`), **`updated_at`** (`TIMESTAMP`).

### `chapters`
- **`id`** (`VARCHAR(36)`, PK): UUID string.
- **`manuscript_id`** (`VARCHAR(36)`, FK -> `manuscripts.id`, `ON DELETE CASCADE`): Parent manuscript.
- **`chapter_number`** (`INTEGER`): 1-indexed sequential chapter order.
- **`title`** (`VARCHAR(255)`): Chapter heading or name.
- **`created_at`** (`TIMESTAMP`), **`updated_at`** (`TIMESTAMP`).

### `chapter_versions`
- **`id`** (`VARCHAR(36)`, PK): UUID string.
- **`chapter_id`** (`VARCHAR(36)`, FK -> `chapters.id`, `ON DELETE CASCADE`): Parent chapter.
- **`version_number`** (`INTEGER`): Monotonically increasing revision number (1, 2, ...).
- **`is_current`** (`BOOLEAN`): True only for the active latest version.
- **`content_path`** (`TEXT`): File path to chapter text snapshot.
- **`content_hash`** (`VARCHAR(64)`): SHA-256 hash of content bytes.
- **`created_at`** (`TIMESTAMP`).

---

## 3. Jobs & Extraction Run Provenance

### `processing_jobs`
- **`id`** (`VARCHAR(36)`, PK): UUID string.
- **`world_id`** (`VARCHAR(36)`, FK -> `worlds.id`, `ON DELETE CASCADE`).
- **`manuscript_id`** (`VARCHAR(36)`, FK -> `manuscripts.id`, `ON DELETE SET NULL`).
- **`job_type`** (`VARCHAR(50)`): `INITIAL_EXTRACTION` | `RE_EXTRACTION`.
- **`status`** (`VARCHAR(50)`): `queued` | `processing` | `done` | `failed`.
- **`chapters_total`** (`INTEGER`): Number of chapters in this job.
- **`chapters_completed`** (`INTEGER`): Number of finished child runs.
- **`error_message`** (`TEXT`, NULL): Failure diagnostic message.
- **`created_at`**, **`started_at`**, **`completed_at`**.

### `extraction_runs`
- **`id`** (`VARCHAR(36)`, PK): UUID string.
- **`chapter_version_id`** (`VARCHAR(36)`, FK -> `chapter_versions.id`, `ON DELETE CASCADE`).
- **`processing_job_id`** (`VARCHAR(36)`, FK -> `processing_jobs.id`, `ON DELETE SET NULL`).
- **`status`** (`VARCHAR(50)`): `pending` | `processing` | `done` | `failed`.
- **`extractor_version`** (`VARCHAR(100)`): Model tag, e.g. `llama3.1:8b`.
- **`created_by`** (`VARCHAR(36)`, FK -> `users.id`, `ON DELETE SET NULL`).
- **`created_at`**, **`started_at`**, **`completed_at`**, **`error_message`**.

---

## 4. Entity & Fact Tables

### `entities`
- **`id`** (`VARCHAR(36)`, PK): UUID string.
- **`world_id`** (`VARCHAR(36)`, FK -> `worlds.id`, `ON DELETE CASCADE`).
- **`entity_type`** (`VARCHAR(50)`): `character` | `location` | `object` | `organization` | `other`.
- **`canonical_name`** (`VARCHAR(255)`): Standardized entity name.
- **`provenance`** (`TEXT`, NULL): Source chunk IDs.
- **`created_at`**, **`updated_at`**.

### `entity_aliases`
- **`id`** (`VARCHAR(36)`, PK): UUID string.
- **`entity_id`** (`VARCHAR(36)`, FK -> `entities.id`, `ON DELETE CASCADE`).
- **`alias`** (`VARCHAR(255)`): Recognized alternative surface name.
- **`confidence`** (`FLOAT`): Match confidence score.

### `facts` & `fact_versions`
- **`facts`**:
  - `id` (PK), `entity_id` (FK -> `entities.id`), `property_name` (`VARCHAR(255)`), `created_at`.
- **`fact_versions`**:
  - `id` (PK), `fact_id` (FK -> `facts.id`).
  - `chapter_id`, `chapter_version_id`, `extraction_run_id` (Nullable FKs).
  - `value` (`JSON`): Extracted attribute value.
  - `status` (`VARCHAR(50)`): `ACTIVE` | `SUPERSEDED` | `CONTRADICTED`.
  - `confidence` (`FLOAT`), `created_at` (`TIMESTAMP`).

---

## 5. Relationships & Events

### `relationships` & `relationship_versions`
- **`relationships`**: `id` (PK), `world_id` (FK), `source_entity_id` (FK), `target_entity_id` (FK), `created_at`.
- **`relationship_versions`**: `id` (PK), `relationship_id` (FK), `chapter_id`, `relationship_type` (`VARCHAR(100)`), `status` (`ACTIVE`/`SUPERSEDED`/`CONTRADICTED`), `confidence`, `created_at`.

### `events` & `event_participants`
- **`events`**: `id` (PK), `world_id` (FK), `chapter_id` (FK), `event_type` (`VARCHAR(100)`), `description` (`TEXT`), `start_position`, `end_position`, `confidence`, `created_at`.
- **`event_participants`**: `id` (PK), `event_id` (FK), `entity_id` (FK), `role` (`VARCHAR(100)`).

---

## 6. Consistency & Contradictions

### `contradictions`
- **`id`** (`VARCHAR(36)`, PK): UUID string.
- **`world_id`** (`VARCHAR(36)`, FK -> `worlds.id`, `ON DELETE CASCADE`).
- **`contradiction_type`** (`VARCHAR(50)`): `FACT_FACT` | `RELATIONSHIP_RELATIONSHIP` | `TEMPORAL` | `EVENT_LOCATION` | `CYCLE`.
- **`old_fact_version_id`**, **`new_fact_version_id`** (FKs -> `fact_versions.id`).
- **`old_relationship_version_id`**, **`new_relationship_version_id`** (FKs -> `relationship_versions.id`).
- **`event_id_a`**, **`event_id_b`** (FKs -> `events.id`).
- **`explanation`** (`TEXT`): Human-readable explanation of why the conflict exists.
- **`confidence`** (`FLOAT`): Confidence score (0.0 to 1.0).
- **`status`** (`VARCHAR(50)`): `DETECTED` | `RESOLVED` | `DISMISSED`.
- **`created_at`** (`TIMESTAMP`).
