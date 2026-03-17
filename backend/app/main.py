from pathlib import Path
from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .celery_app import celery_app
from .schemas import DatetimeToTimestampRequest, VideoEditManifest
from .storage import StorageManager

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

from .engine.j2v_types import J2VMovie

@app.post("/tasks/j2v-render")
def create_j2v_render_task(manifest: J2VMovie) -> dict:
    """Trigger the J2V Local Clone rendering process."""
    # We can either run it synchronously for small tests or use Celery.
    # For now, let's use Celery to keep the API responsive.
    async_result = celery_app.send_task(
        "kombajn.tasks.j2v_render_movie",
        kwargs={"manifest_dict": manifest.model_dump(by_alias=True)},
    )
    return {"task_id": async_result.id}

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str) -> dict:
    result = AsyncResult(task_id, app=celery_app)
    payload: dict = {
        "task_id": task_id,
        "state": result.state,
        "ready": result.ready(),
        "successful": result.successful(),
    }
    if result.successful():
        payload["result"] = result.result
    return payload
