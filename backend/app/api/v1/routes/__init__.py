from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.worlds import router as worlds_router
from app.api.v1.routes.manuscripts import router as manuscripts_router
from app.api.v1.routes.chapters import router as chapters_router
from app.api.v1.routes.jobs import router as jobs_router
from app.api.v1.routes.entities import router as entities_router
from app.api.v1.routes.graph import router as graph_router
from app.api.v1.routes.timeline import router as timeline_router
from app.api.v1.routes.contradictions import router as contradictions_router
from app.api.v1.routes.chat import router as chat_router
from app.api.v1.routes.relationships import router as relationships_router
from app.api.v1.routes.events import router as events_router
from app.api.v1.routes.proposals import router as proposals_router

__all__ = [
    "auth_router",
    "worlds_router",
    "manuscripts_router",
    "chapters_router",
    "jobs_router",
    "entities_router",
    "graph_router",
    "timeline_router",
    "contradictions_router",
    "chat_router",
    "relationships_router",
    "events_router",
    "proposals_router",
]
