
import json
import os

from chunker import chunk_text
from extractor import extract_from_chunk
from validator import validate_extraction
from entity_resolver import resolve_entities
from world_state_integrator import integrate_world_state
from consistency_checker import check_consistency


# ============================================================
# CONFIGURATION
# ============================================================

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# DISPLAY FUNCTIONS
# ============================================================

def print_banner():

    print()
    print("=" * 65)
    print("              WORLD STATE ENGINE")
    print("              Local LLM Pipeline")
    print("=" * 65)


def print_extraction_summary(
    chunk_id,
    extraction,
    errors
):

    print()
    print("-" * 65)
    print(f"CHUNK: {chunk_id}")
    print("-" * 65)

    if errors:

        print("STATUS: INVALID")

        for error in errors:
            print(f"  - {error}")

        return

    print("STATUS: VALID")
    print()

    print(
        f"Entities:          "
        f"{len(extraction.get('entities', []))}"
    )

    print(
        f"Relationships:     "
        f"{len(extraction.get('relationships', []))}"
    )

    print(
        f"Events:            "
        f"{len(extraction.get('events', []))}"
    )

    print(
        f"State changes:     "
        f"{len(extraction.get('state_changes', []))}"
    )

    print(
        f"Temporal relations:"
        f" {len(extraction.get('temporal_relations', []))}"
    )

    print(
        f"Attributions:      "
        f"{len(extraction.get('attributions', []))}"
    )


def print_entity_resolution(resolution):

    print()
    print("=" * 65)
    print("                    ENTITY RESOLUTION")
    print("=" * 65)

    mentions = resolution.get(
        "mentions",
        []
    )

    entities = resolution.get(
        "entities",
        []
    )

    print()
    print(
        f"Raw entity mentions: "
        f"{len(mentions)}"
    )

    print(
        f"Canonical entities:  "
        f"{len(entities)}"
    )

    contextual = resolution.get(
        "contextual_resolution",
        {},
    )

    if contextual.get("sent", 0):
        print()
        print("Contextual resolution:")
        print(f"    Sent to local LLM: {contextual['sent']}")
        print(f"    MATCH:             {contextual['match']}")
        print(f"    NEW_ENTITY:        {contextual['new_entity']}")
        print(f"    UNRESOLVED:        {contextual['unresolved']}")

    print()

    for entity in entities:

        entity_id = entity.get(
            "entity_id",
            "UNKNOWN"
        )

        canonical_name = entity.get(
            "canonical_name",
            "UNKNOWN"
        )

        entity_type = entity.get(
            "type",
            "OTHER"
        )

        aliases = entity.get(
            "aliases",
            []
        )

        print(
            f"{entity_id}: "
            f"{canonical_name} "
            f"[{entity_type}]"
        )

        print(
            f"    aliases: "
            f"{', '.join(aliases)}"
        )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print_banner()

    # --------------------------------------------------------
    # 1. LOAD MANUSCRIPT
    # --------------------------------------------------------

    print()
    print("[1/5] Loading manuscript...")

    try:

        manuscript = load_manuscript()

    except Exception as error:

        print()
        print("ERROR:")
        print(error)
        return

    print(
        f"Loaded manuscript: "
        f"{len(manuscript):,} characters"
    )


    # --------------------------------------------------------
    # 2. CHUNKING
    # --------------------------------------------------------

    print()
    print("[2/5] Chunking manuscript...")

    chunks = chunk_text(
        manuscript
    )

    print(
        f"Generated {len(chunks)} chunks"
    )


    # --------------------------------------------------------
    # 3. LLM EXTRACTION
    # --------------------------------------------------------

    print()
    print("[3/5] Running LLM extraction...")
    print()
    print(
        "Model: llama3.1:8b-instruct-q4_K_M"
    )

    all_extractions = []

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        chunk_id = f"chunk_{index:03d}"

        print()
        print(
            f"[{index}/{len(chunks)}] "
            f"Processing {chunk_id}..."
        )

        try:

            extraction = extract_from_chunk(
                chunk,
                chunk_id
            )

            errors = validate_extraction(
                extraction
            )

            print_extraction_summary(
                chunk_id,
                extraction,
                errors
            )

            all_extractions.append(
                {
                    "chunk_id": chunk_id,

                    "extraction": extraction,

                    "validation_errors": errors
                }
            )

        except Exception as error:

            print()
            print(
                f"EXTRACTION FAILED "
                f"for {chunk_id}"
            )

            print(
                f"Error: {error}"
            )

            all_extractions.append(
                {
                    "chunk_id": chunk_id,

                    "extraction": None,

                    "validation_errors": [
                        str(error)
                    ]
                }
            )


    # --------------------------------------------------------
    # 4. SAVE RAW EXTRACTION
    # --------------------------------------------------------

    print()
    print("[4/5] Saving raw extraction...")

    save_json(
        OUTPUT_EXTRACTION,
        all_extractions
    )

    print(
        f"Saved: {OUTPUT_EXTRACTION}"
    )


    # --------------------------------------------------------
    # 5. ENTITY RESOLUTION
    # --------------------------------------------------------

    print()
    print("[5/5] Resolving entities...")

    try:

        resolution = resolve_entities(
            all_extractions
        )

    except Exception as error:

        print()
        print(
            "ENTITY RESOLUTION FAILED"
        )

        print(
            f"Error: {error}"
            "UNKNOWN"
        )

        canonical_name = entity.get(
            "canonical_name",
            "UNKNOWN"
        )

        entity_type = entity.get(
            "type",
            "OTHER"
        )

        aliases = entity.get(
            "aliases",
            []
        )

        print(
            f"{entity_id}: "
            f"{canonical_name} "
            f"[{entity_type}]"
        )

        print(
            f"    aliases: "
            f"{', '.join(aliases)}"
        )


def run_extraction(manuscript: str, world_id: str, job_id: str, extraction_run_id: str = None, chapter_id: str = None, chapter_version_id: str = None):
    from database import SessionLocal
    import models
    import datetime
    import json
    
    db = SessionLocal()
    try:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if job:
            job.status = "processing"
            job.started_at = datetime.datetime.utcnow()
            db.commit()
            
        print_banner()

        # --------------------------------------------------------
        # 2. CHUNKING
        # --------------------------------------------------------

        print()
        print("[2/5] Chunking manuscript...")

        chunks = chunk_text(
            manuscript
        )

        print(
            f"Generated {len(chunks)} chunks"
        )
        
        if job:
            job.progress_total = len(chunks)
            db.commit()

        # --------------------------------------------------------
        # 3. LLM EXTRACTION
        # --------------------------------------------------------

        print()
        print("[3/5] Running LLM extraction...")
        
        all_extractions = []

        for index, chunk in enumerate(
            chunks,
            start=1
        ):
            chunk_id = f"chunk_{index:03d}"
            print(f"[{index}/{len(chunks)}] Processing {chunk_id}...")

            try:
                extraction = extract_from_chunk(chunk, chunk_id)
                errors = validate_extraction(extraction)
                all_extractions.append({
                    "chunk_id": chunk_id,
                    "extraction": extraction,
                    "validation_errors": errors
                })
            except Exception as error:
                all_extractions.append({
                    "chunk_id": chunk_id,
                    "extraction": None,
                    "validation_errors": [str(error)]
                })

            if job:
                job.progress_current = index
                db.commit()

        # --------------------------------------------------------
        # 4. SAVE RAW EXTRACTION
        # --------------------------------------------------------

        save_json(OUTPUT_EXTRACTION, all_extractions)

        # --------------------------------------------------------
        # 5. ENTITY RESOLUTION
        # --------------------------------------------------------

        print("[5/5] Resolving entities...")
        try:
            resolution = resolve_entities(all_extractions)
        except Exception as error:
            print("ENTITY RESOLUTION FAILED")
            if job:
                job.status = "failed"
                job.error_message = str(error)
                db.commit()
            return

        # --------------------------------------------------------
        # BUILD WORLD STATE
        # --------------------------------------------------------

        metadata = {
            "source_file": "API Upload",
            "num_chunks": len(chunks),
            "pipeline": ["chunking", "llm_extraction", "validation", "entity_resolution", "world_state_integration"]
        }

        print("[6/7] Integrating world state...")
        world_state = integrate_world_state(
            metadata=metadata,
            entities=resolution.get("entities", []),
            mentions=resolution.get("mentions", []),
            contextual_resolution=resolution.get("contextual_resolution", {}),
            extractions=all_extractions
        )
        
        # --------------------------------------------------------
        # DB INSERTION TRANSLATION STEP
        # --------------------------------------------------------
        print("[7/7] Inserting to database...")
        
        # Insert Entities
        ent_map = {}
        for ent_data in world_state.get("entities", []):
            pipeline_id = ent_data.get("id", ent_data.get("entity_id"))
            canonical = ent_data.get("canonical_name", "UNKNOWN")
            
            # 1. Try to find existing entity by canonical name
            existing_ent = db.query(models.Entity).filter(
                models.Entity.world_id == world_id,
                models.Entity.canonical_name == canonical
            ).first()
            
            # 2. Try to find by alias (if no match yet)
            if not existing_ent:
                aliases = ent_data.get("aliases", [])
                if aliases:
                    alias_match = db.query(models.EntityAlias).join(
                        models.Entity, models.EntityAlias.entity_id == models.Entity.id
                    ).filter(
                        models.Entity.world_id == world_id,
                        models.EntityAlias.alias.in_(aliases)
                    ).first()
                    if alias_match:
                        # get the full entity object
                        existing_ent = db.query(models.Entity).filter(models.Entity.id == alias_match.entity_id).first()
            
            if existing_ent:
                ent_map[pipeline_id] = existing_ent
                
                # Add new aliases if not exist
                existing_aliases = {a.alias for a in db.query(models.EntityAlias).filter_by(entity_id=existing_ent.id).all()}
                for alias in ent_data.get("aliases", []):
                    if alias not in existing_aliases:
                        new_alias = models.EntityAlias(entity_id=existing_ent.id, alias=alias, confidence=1.0)
                        db.add(new_alias)
                db.commit()
            else:
                # Create new (ID will be fresh UUID as defined in models.py default)
                ent = models.Entity(
                    world_id=world_id,
                    entity_type=ent_data.get("type", "UNKNOWN"),
                    canonical_name=canonical,
                    source_extraction_id=pipeline_id,
                    provenance=json.dumps(ent_data.get("source_chunk_ids", []))
                )
                db.add(ent)
                db.commit()
                db.refresh(ent)
                ent_map[pipeline_id] = ent
                
                for alias in ent_data.get("aliases", []):
                    new_alias = models.EntityAlias(entity_id=ent.id, alias=alias, confidence=1.0)
                    db.add(new_alias)
                db.commit()
            
            # --- FACT INSERTION ---
            attributes = ent_data.get("attributes", {})
            if isinstance(attributes, dict):
                target_entity_id = ent_map[pipeline_id].id
                for prop_name, value in attributes.items():
                    fact = db.query(models.Fact).filter(
                        models.Fact.entity_id == target_entity_id,
                        models.Fact.property_name == prop_name
                    ).first()
                    
                    if not fact:
                        fact = models.Fact(
                            entity_id=target_entity_id,
                            property_name=prop_name
                        )
                        db.add(fact)
                        db.commit()
                        db.refresh(fact)
                        
                    fact_version = models.FactVersion(
                        fact_id=fact.id,
                        chapter_id=chapter_id,
                        chapter_version_id=chapter_version_id,
                        extraction_run_id=extraction_run_id,
                        value=value,
                        status="ACTIVE",
                        confidence=1.0
                    )
                    db.add(fact_version)
                db.commit()
        
        # Insert Relationships
        for rel_data in world_state.get("relationships", []):
            subj_pipeline_id = rel_data.get("subject", {}).get("entity_id")
            obj_pipeline_id = rel_data.get("object", {}).get("entity_id")
            rel_type = rel_data.get("type", "Unknown")
            rel_pipeline_id = rel_data.get("relationship_id")
            
            if subj_pipeline_id in ent_map and obj_pipeline_id in ent_map:
                subj_db = ent_map[subj_pipeline_id]
                obj_db = ent_map[obj_pipeline_id]
                
                rel = models.Relationship(
                    world_id=world_id,
                    source_entity_id=subj_db.id,
                    target_entity_id=obj_db.id,
                    source_extraction_id=rel_pipeline_id
                )
                db.add(rel)
                db.commit()
                db.refresh(rel)
                
                rel_ver = models.RelationshipVersion(
                    relationship_id=rel.id,
                    chapter_id=chapter_id,
                    chapter_version_id=chapter_version_id,
                    extraction_run_id=extraction_run_id,
                    relationship_type=rel_type,
                    status="ACTIVE",
                    confidence=rel_data.get("confidence", 1.0)
                )
                db.add(rel_ver)
                db.commit()
                
        # Insert Events
        for event_data in world_state.get("events", []):
            event = models.Event(
                world_id=world_id,
                chapter_id=chapter_id,
                chapter_version_id=chapter_version_id,
                extraction_run_id=extraction_run_id,
                event_type=event_data.get("type", "UNKNOWN"),
                description=event_data.get("description", ""),
                confidence=event_data.get("confidence", 1.0)
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            
            for part in event_data.get("participants", []):
                part_pipeline_id = part.get("entity_id")
                if part_pipeline_id in ent_map:
                    part_db = ent_map[part_pipeline_id]
                    ep = models.EventParticipant(
                        event_id=event.id,
                        entity_id=part_db.id,
                        role=part.get("role", "UNKNOWN")
                    )
                    db.add(ep)
            db.commit()
                
        # --------------------------------------------------------
        # SAVE WORLD STATE
        # --------------------------------------------------------

        save_json(OUTPUT_WORLD_STATE, world_state)
        
        if job:
            job.status = "done"
            job.completed_at = datetime.datetime.utcnow()
            db.commit()
            
        if extraction_run_id:
            ext_run = db.query(models.ExtractionRun).filter_by(id=extraction_run_id).first()
            if ext_run:
                ext_run.status = "done"
                ext_run.completed_at = datetime.datetime.utcnow()
                db.commit()

        print("PIPELINE COMPLETE")
        
    except Exception as e:
        print(f"PIPELINE ERROR: {e}")
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
            
        if extraction_run_id:
            ext_run = db.query(models.ExtractionRun).filter_by(id=extraction_run_id).first()
            if ext_run:
                ext_run.status = "failed"
                ext_run.error_message = str(e)
                db.commit()
    finally:
        db.close()

# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    pass
