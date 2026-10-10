// Owner: Person B (feature/graph-timeline). Contract: docs/api.md §9 and §15.
import { notImplemented } from './stub';

export interface EventParticipantResponse {
  entity_id: string;
  entity_name: string | null;
  role: string;
}

/** Same shape as a timeline event (TimelineEventResponse). */
export interface EventResponse {
  id: string;
  world_id: string;
  chapter_id: string | null;
  chapter_number: number | null;
  event_type: string;
  description: string;
  start_position: number | null;
  end_position: number | null;
  sequence_index: number | null;
  confidence: number;
  created_at: string;
  participants: EventParticipantResponse[];
}

export interface TimelineResponse {
  events: EventResponse[];
  total: number;
}

export interface EventParticipantInput {
  entity_id: string;
  role?: string;
}

/** §15.1 */
export interface EventCreateRequest {
  description: string;
  event_type?: string;
  chapter_id?: string | null;
  sequence_index?: number | null;
  participants?: EventParticipantInput[];
}

/** §15.3: any subset; `participants` replaces the whole list. */
export interface EventUpdateRequest {
  description?: string;
  event_type?: string;
  chapter_id?: string | null;
  participants?: EventParticipantInput[];
}

/** §15.5: every event in the chapter, exactly once, in the new order. */
export interface EventReorderRequest {
  chapter_id: string | null;
  event_ids: string[];
}

/** GET /worlds/{worldId}/timeline → 200 (§9.1) */
export const getTimeline: (worldId: string) => Promise<TimelineResponse> = notImplemented('getTimeline');

/** GET /worlds/{worldId}/events/{eventId} → 200 (§15.2) */
export const getEvent: (worldId: string, eventId: string) => Promise<EventResponse> = notImplemented('getEvent');

/** POST /worlds/{worldId}/events → 201 (§15.1) */
export const createEvent: (worldId: string, body: EventCreateRequest) => Promise<EventResponse> =
  notImplemented('createEvent');

/** PUT /worlds/{worldId}/events/{eventId} → 200 (§15.3) */
export const updateEvent: (worldId: string, eventId: string, body: EventUpdateRequest) => Promise<EventResponse> =
  notImplemented('updateEvent');

/** DELETE /worlds/{worldId}/events/{eventId} → 204 (§15.4) */
export const deleteEvent: (worldId: string, eventId: string) => Promise<void> = notImplemented('deleteEvent');

/** PATCH /worlds/{worldId}/events/reorder → 200, that chapter's events in the new order (§15.5) */
export const reorderEvents: (worldId: string, body: EventReorderRequest) => Promise<TimelineResponse> =
  notImplemented('reorderEvents');
