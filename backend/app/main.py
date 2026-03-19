from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .api import health, tasks

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="KOMBAJN AI - Sprint 1 API")

app.include_router(health.router)
app.include_router(tasks.router, prefix="/tasks")

@app.get("/", response_class=HTMLResponse)
def landing() -> HTMLResponse:
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
