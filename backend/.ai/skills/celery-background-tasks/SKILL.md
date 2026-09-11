---
name: celery-background-tasks
description: Recipe for creating, scheduling, and testing asynchronous Celery worker tasks with Redis.
---

# Skill: Celery & Background Worker Tasks

Follow this recipe when introducing long-running asynchronous jobs or scheduling background routines.

---

## 1. Task Definition Protocol

Define worker tasks inside [`app/workers/tasks/`](../../app/workers/tasks/):

```python
# app/workers/tasks/export_task.py
from app.workers.celery_app import celery_app
from app.config.logging import get_logger

logger = get_logger(__name__)

def execute_export_pdf(world_id: str, output_path: str) -> str:
    # Pure Python logic decoupled from Celery
    ...
    return output_path

@celery_app.task(bind=True, name="tasks.export_pdf", max_retries=3)
def export_pdf_task(self, world_id: str, output_path: str):
    try:
        return execute_export_pdf(world_id, output_path)
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc, countdown=10)
```

**Rule**: Always decouple the task implementation into a pure Python function (`execute_*`) and a Celery decorator wrapper (`@celery_app.task`). This allows immediate synchronous execution during testing or when Redis is absent.

---

## 2. Dispatching Tasks from API Routes

```python
# Route handler
from app.workers.tasks.export_task import export_pdf_task, execute_export_pdf

@router.post("/worlds/{world_id}/export")
def trigger_export(world_id: str, background_tasks: BackgroundTasks):
    try:
        # Preferred: Celery queue
        task = export_pdf_task.delay(world_id, output_path)
        return {"task_id": task.id}
    except Exception:
        # Fallback: Local BackgroundTasks
        background_tasks.add_task(execute_export_pdf, world_id, output_path)
        return {"status": "processing_locally"}
```

---

## 3. Running Workers Locally

```bash
# Terminal 1: Start Redis container
docker run -p 6379:6379 redis:7-alpine

# Terminal 2: Start Celery worker
cd backend
celery -A app.workers.celery_app worker --loglevel=info -c 2
```

---

## Verification

Test task execution directly without spinning up worker infrastructure:
```python
def test_export_task_direct():
    result = execute_export_pdf(world_id="test", output_path="/tmp/test.pdf")
    assert result == "/tmp/test.pdf"
```
