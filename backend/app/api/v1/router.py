from fastapi import APIRouter

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

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(worlds_router, prefix="/worlds", tags=["Worlds"])
api_router.include_router(manuscripts_router, prefix="/worlds", tags=["Manuscripts"])
api_router.include_router(chapters_router, prefix="/worlds", tags=["Chapters"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(entities_router, prefix="/worlds", tags=["Entities & Facts"])
api_router.include_router(graph_router, prefix="/worlds", tags=["Knowledge Graph"])
api_router.include_router(timeline_router, prefix="/worlds", tags=["Timeline"])
api_router.include_router(contradictions_router, prefix="/worlds", tags=["Contradictions"])
api_router.include_router(chat_router, prefix="/worlds", tags=["World Chat"])
