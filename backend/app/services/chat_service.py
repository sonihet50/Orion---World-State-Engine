from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.entity import Entity
from app.models.relationship import Relationship
from app.models.event import Event
from app.models.contradiction import Contradiction
from app.pipeline.llm_client import llm_client
from app.schemas.chat import ChatCitation, ChatMessage, ChatQueryResponse
from app.config.logging import get_logger

logger = get_logger(__name__)

CHAT_PROMPT_FILE = Path(__file__).parent.parent / "pipeline" / "prompts" / "chat_prompt.txt"

def load_chat_system_prompt() -> str:
    if CHAT_PROMPT_FILE.exists():
        with open(CHAT_PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "You are an intelligent assistant for the fictional world state engine."


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.system_prompt = load_chat_system_prompt()

    def query(
        self,
        world_id: str,
        message: str,
        history: List[ChatMessage] = [],
        entity_focus: Optional[str] = None,
        timeline_event_focus: Optional[str] = None
    ) -> ChatQueryResponse:
        # Build contextual snapshot
        entities = self.db.query(Entity).filter(Entity.world_id == world_id).limit(25).all()
        relationships = self.db.query(Relationship).filter(Relationship.world_id == world_id).limit(20).all()
        events = self.db.query(Event).filter(Event.world_id == world_id).limit(15).all()
        contradictions = self.db.query(Contradiction).filter(
            Contradiction.world_id == world_id,
            Contradiction.status == "DETECTED"
        ).all()

        citations: List[ChatCitation] = []

        context_lines = ["CURRENT WORLD STATE CONTEXT:"]

        # Entities & Facts
        context_lines.append("\nENTITIES & KNOWN FACTS:")
        for ent in entities:
            ent_facts = []
            for f in ent.facts:
                latest_ver = f.versions[0] if f.versions else None
                if latest_ver and latest_ver.status == "ACTIVE":
                    ent_facts.append(f"{f.property_name}: {latest_ver.value}")
            facts_str = f" ({', '.join(ent_facts)})" if ent_facts else ""
            context_lines.append(f"- {ent.canonical_name} [{ent.entity_type}]{facts_str}")

            if ent.canonical_name.lower() in message.lower():
                citations.append(ChatCitation(
                    source_type="entity",
                    source_id=ent.id,
                    title=ent.canonical_name,
                    snippet=f"Entity {ent.canonical_name} ({ent.entity_type}){facts_str}"
                ))

        # Relationships
        context_lines.append("\nRELATIONSHIPS:")
        for rel in relationships:
            active_ver = rel.versions[0] if rel.versions else None
            rel_type = active_ver.relationship_type if active_ver else "RELATED_TO"
            s_name = rel.source_entity.canonical_name if rel.source_entity else "Unknown"
            t_name = rel.target_entity.canonical_name if rel.target_entity else "Unknown"
            context_lines.append(f"- {s_name} -> {rel_type} -> {t_name}")

        # Events
        context_lines.append("\nEVENTS:")
        for ev in events:
            context_lines.append(f"- [{ev.event_type}] {ev.description}")
            if ev.description and any(w in ev.description.lower() for w in message.lower().split() if len(w) > 4):
                citations.append(ChatCitation(
                    source_type="event",
                    source_id=ev.id,
                    title=f"Event: {ev.event_type}",
                    snippet=ev.description[:120]
                ))

        # Contradictions
        if contradictions:
            context_lines.append("\nFLAGGED CONTRADICTIONS / CONFLICTS:")
            for con in contradictions:
                context_lines.append(f"- [CONFLICT: {con.contradiction_type}] {con.explanation}")
                citations.append(ChatCitation(
                    source_type="contradiction",
                    source_id=con.id,
                    title=f"Contradiction: {con.contradiction_type}",
                    snippet=con.explanation
                ))

        full_system_context = f"{self.system_prompt}\n\n" + "\n".join(context_lines)

        messages_payload = [{"role": h.role, "content": h.content} for h in history]
        messages_payload.append({"role": "user", "content": message})

        llm_answer = llm_client.chat(
            messages=messages_payload,
            system_prompt=full_system_context,
            temperature=0.3
        )

        suggested_actions = []
        if contradictions:
            suggested_actions.append("Review detected contradictions in the Consistency Panel.")
        suggested_actions.append("Explore entity relationship connections in the Knowledge Graph.")

        return ChatQueryResponse(
            response=llm_answer,
            citations=citations,
            suggested_actions=suggested_actions
        )
