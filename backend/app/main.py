from pathlib import Path
from celery.result import AsyncResult
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .celery_app import celery_app
from .schemas import VideoEditManifest
from .storage import StorageManager
from .engine.j2v_types import J2VMovie

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="KOMBAJN AI - Sprint 0 API")
storage = StorageManager()

@app.get("/", response_class=HTMLResponse)
def landing() -> HTMLResponse:
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))

@app.get("/health/full")
def health_full() -> dict:
    replies = celery_app.control.ping(timeout=1.0)
    return {"status": "ok", "workers": replies}

@app.post("/tasks/j2v-render")
def create_j2v_render_task(manifest: J2VMovie) -> dict:
    """Trigger the J2V Local Clone rendering process."""
    async_result = celery_app.send_task(
        "kombajn.tasks.j2v_render_movie",
        kwargs={"manifest_dict": manifest.model_dump(by_alias=True)},
    )
    return {"task_id": async_result.id}

@app.get("/tasks")
def list_tasks() -> dict:
    i = celery_app.control.inspect()
    # Merge active and reserved tasks to see what's in flight
    active = i.active() or {}
    reserved = i.reserved() or {}
    
    tasks_list = []
    
    for worker_data in [active, reserved]:
        for worker, tasks in worker_data.items():
            for t in tasks:
                tasks_list.append({
                    "task_id": t.get('id'),
                    "status": "ACTIVE" if worker_data == active else "RESERVED",
                    "timestamp": t.get('time_start', 'N/A')
                })
    return {"tasks": tasks_list}
