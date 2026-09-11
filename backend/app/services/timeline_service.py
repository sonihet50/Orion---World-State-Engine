from typing import List
from sqlalchemy.orm import Session

from app.repositories.event_repo import EventRepository
from app.schemas.timeline import TimelineEventResponse, TimelineResponse, TimelineParticipant

class TimelineService:
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)

    def get_world_timeline(self, world_id: str) -> TimelineResponse:
        events = self.event_repo.list_by_world(world_id)

        responses: List[TimelineEventResponse] = []
        for ev in events:
            participants = []
            for p in ev.participants:
                ent_name = p.entity.canonical_name if p.entity else None
                participants.append(TimelineParticipant(
                    entity_id=p.entity_id,
                    entity_name=ent_name,
                    role=p.role
                ))

            ch_num = ev.chapter.chapter_number if ev.chapter else None

            responses.append(TimelineEventResponse(
                id=ev.id,
                world_id=ev.world_id,
                chapter_id=ev.chapter_id,
                chapter_number=ch_num,
                event_type=ev.event_type,
                description=ev.description,
                start_position=ev.start_position,
                end_position=ev.end_position,
                confidence=ev.confidence,
                created_at=ev.created_at,
                participants=participants
            ))

        return TimelineResponse(events=responses, total=len(responses))
