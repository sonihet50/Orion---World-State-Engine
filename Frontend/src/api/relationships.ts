// Owner: Person B (feature/graph-timeline). Contract: docs/api.md §14.
import type { VersionStatus } from './entities';
import { notImplemented } from './stub';

export interface RelationshipVersionResponse {
  id: string;
  relationship_id: string;
  relationship_type: string;
  status: VersionStatus;
  chapter_id: string | null;
  chapter_number: number | null;
  confidence: number;
  created_at: string;
}

export interface RelationshipResponse {
  id: string;
  world_id: string;
  source_entity_id: string;
  source_name: string;
  target_entity_id: string;
  target_name: string;
  created_at: string;
  /** Latest ACTIVE version, or null if none is active. */
  current_version: RelationshipVersionResponse | null;
  /** Every version, newest first. */
  versions: RelationshipVersionResponse[];
}

/** §14.3 */
export interface RelationshipCreateRequest {
  source_entity_id: string;
  target_entity_id: string;
  relationship_type: string;
  chapter_id?: string | null;
  confidence?: number;
}

/** §14.4 */
export interface RelationshipUpdateRequest {
  relationship_type: string;
  chapter_id?: string | null;
  confidence?: number;
}

export interface ListRelationshipsParams {
  entity_id?: string;
}

/** GET /worlds/{worldId}/relationships → 200 (§14.1) */
export const listRelationships: (worldId: string, params?: ListRelationshipsParams) => Promise<RelationshipResponse[]> =
  notImplemented('listRelationships');

/** GET /worlds/{worldId}/relationships/{relationshipId} → 200 (§14.2) */
export const getRelationship: (worldId: string, relationshipId: string) => Promise<RelationshipResponse> =
  notImplemented('getRelationship');

/** POST /worlds/{worldId}/relationships → 201 new pair, 200 new version on an existing pair (§14.3) */
export const createRelationship: (worldId: string, body: RelationshipCreateRequest) => Promise<RelationshipResponse> =
  notImplemented('createRelationship');

/** PUT /worlds/{worldId}/relationships/{relationshipId} → 200 (§14.4) */
export const updateRelationship: (
  worldId: string,
  relationshipId: string,
  body: RelationshipUpdateRequest,
) => Promise<RelationshipResponse> = notImplemented('updateRelationship');

/** DELETE /worlds/{worldId}/relationships/{relationshipId} → 204 (§14.5) */
export const deleteRelationship: (worldId: string, relationshipId: string) => Promise<void> =
  notImplemented('deleteRelationship');
