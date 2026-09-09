from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
from main import run_extraction

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel
from typing import Optional

class WorldCreate(BaseModel):
    name: str
    description: Optional[str] = ""

@app.post("/worlds")
def create_world(world_in: WorldCreate, db: Session = Depends(get_db)):
    world = models.World(name=world_in.name, description=world_in.description)
    db.add(world)
    db.commit()
    db.refresh(world)
    return {"id": world.id, "name": world.name, "description": world.description}

@app.get("/worlds")
def list_worlds(db: Session = Depends(get_db)):
    worlds = db.query(models.World).order_by(models.World.created_at.desc()).all()
    return [{"id": w.id, "name": w.name, "description": w.description, "created_at": w.created_at} for w in worlds]

@app.get("/worlds/{world_id}")
def get_world(world_id: str, db: Session = Depends(get_db)):
    world = db.query(models.World).filter(models.World.id == world_id).first()
    if not world:
        raise HTTPException(status_code=404, detail="World not found")
    return {"id": world.id, "name": world.name, "description": world.description, "created_at": world.created_at}

import hashlib

@app.post("/worlds/{world_id}/manuscripts", status_code=202)
async def upload_manuscript(
    world_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    world = db.query(models.World).filter(models.World.id == world_id).first()
    if not world:
        raise HTTPException(status_code=404, detail="World not found")

    content = await file.read()
    text = content.decode('utf-8')
    content_hash = hashlib.sha256(content).hexdigest()

    manuscript = models.Manuscript(world_id=world_id, title=file.filename, file_type=file.content_type)
    db.add(manuscript)
    db.commit()
    db.refresh(manuscript)

    version = models.ManuscriptVersion(manuscript_id=manuscript.id, version_number=1, content=text)
    db.add(version)

    chapter = models.Chapter(manuscript_id=manuscript.id, chapter_number=1, title="Chapter 1")
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    chapter_version = models.ChapterVersion(
        chapter_id=chapter.id, 
        version_number=1, 
        is_current=True, 
        content_hash=content_hash
    )
    db.add(chapter_version)
    db.commit()
    db.refresh(chapter_version)

    job = models.Job(world_id=world_id, manuscript_id=manuscript.id, type="INITIAL_EXTRACTION", status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)

    extraction_run = models.ExtractionRun(
        chapter_version_id=chapter_version.id, 
        processing_job_id=job.id, 
        status="processing",
        extractor_version="llama3.1:8b"
    )
    db.add(extraction_run)
    db.commit()
    db.refresh(extraction_run)

    background_tasks.add_task(
        run_extraction, 
        text, 
        world_id, 
        job.id, 
        extraction_run.id, 
        chapter.id, 
        chapter_version.id
    )

    return {"job_id": job.id}

@app.get("/jobs/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": job.id,
        "status": job.status,
        "progress_current": job.progress_current,
        "progress_total": job.progress_total,
        "error_message": job.error_message
    }

@app.get("/worlds/{world_id}/entities")
def get_world_entities(world_id: str, db: Session = Depends(get_db)):
    entities = db.query(models.Entity).filter(models.Entity.world_id == world_id).all()
    relationships = db.query(models.Relationship).filter(models.Relationship.world_id == world_id).all()

    rels_out = []
    for rel in relationships:
        latest_version = db.query(models.RelationshipVersion).filter(
            models.RelationshipVersion.relationship_id == rel.id
        ).order_by(models.RelationshipVersion.created_at.desc()).first()

        rels_out.append({
            "id": rel.id,
            "source_entity_id": rel.source_entity_id,
            "target_entity_id": rel.target_entity_id,
            "type": latest_version.relationship_type if latest_version else "Unknown",
            "confidence": latest_version.confidence if latest_version else 1.0
        })

    ents_out = []
    for ent in entities:
        ents_out.append({
            "id": ent.id,
            "entity_type": ent.entity_type,
            "canonical_name": ent.canonical_name,
            "provenance": ent.provenance
        })

    return {
        "entities": ents_out,
        "relationships": rels_out
    }
