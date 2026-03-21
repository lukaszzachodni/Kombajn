import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from .api import health, render_task, list_tasks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="KOMBAJN AI - Production API")

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal Server Error",
            "detail": str(exc),
            "path": request.url.path
        }
    )

app.include_router(health.router)
app.include_router(render_task.router, prefix="/tasks")
app.include_router(list_tasks.router, prefix="/tasks")

@app.get("/", response_class=HTMLResponse)
def landing() -> HTMLResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse(content="<h1>KOMBAJN AI API</h1><p>Static index.html not found.</p>", status_code=404)
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
