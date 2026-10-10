// Owner: Extraction (feature/extraction-review). Contract: docs/api.md §17.
import type { AliasCreateRequest, EntityCreateRequest, FactCreateRequest } from './entities';
import type { EventCreateRequest } from './events';
import { notImplemented } from './stub';

export type ProposalChange = 'new' | 'changed' | 'known';

/** An existing entity, or the entity created by a `new` entity proposal in the same response. */
export type EntityRef = { entity_id: string } | { entity_ref: string };

interface ProposalBase {
  /** Unique within the response; other proposals point at it through `entity_ref`. */
  id: string;
  change: ProposalChange;
  summary: string;
  confidence: number;
}

export interface EntityProposal extends ProposalBase {
  kind: 'entity';
  change: 'new' | 'known';
  match_entity_id: string | null;
  proposed: EntityCreateRequest;
}

export interface AliasProposal extends ProposalBase {
  kind: 'alias';
  change: 'new' | 'known';
  entity_id: string;
  proposed: AliasCreateRequest;
}

export interface FactProposal extends ProposalBase {
  kind: 'fact';
  entity: EntityRef;
  current: { fact_version_id: string; value: unknown } | null;
  proposed: FactCreateRequest;
}

export interface RelationshipProposal extends ProposalBase {
  kind: 'relationship';
  source: EntityRef;
  target: EntityRef;
  current: { relationship_id: string; relationship_version_id: string; relationship_type: string } | null;
  proposed: { relationship_type: string; chapter_id: string | null; confidence: number };
}

export interface EventProposal extends ProposalBase {
  kind: 'event';
  change: 'new' | 'known';
  participants: { entity: EntityRef; role: string }[];
  proposed: Omit<EventCreateRequest, 'participants'>;
}

export type Proposal = EntityProposal | AliasProposal | FactProposal | RelationshipProposal | EventProposal;

export interface ProposalsResponse {
  job_id: string;
  world_id: string;
  chapter_id: string | null;
  chapter_number: number | null;
  /** `pending` comes with HTTP 202 and an empty list while the job is queued or processing. */
  status: 'pending' | 'ready';
  generated_at: string | null;
  proposals: Proposal[];
}

/** Apply order for the review modal (§17): entity refs must exist before anything points at them. */
export const PROPOSAL_APPLY_ORDER: Proposal['kind'][] = ['entity', 'alias', 'fact', 'relationship', 'event'];

/** GET /jobs/{jobId}/proposals → 200 ready, 202 pending (§17.1) */
export const getProposals: (jobId: string) => Promise<ProposalsResponse> = notImplemented('getProposals');
