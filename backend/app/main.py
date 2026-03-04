from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .celery_app import celery_app
from .storage import StorageManager


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="KOMBAJN AI - Sprint 0 API")

storage = StorageManager()


@app.get("/", response_class=HTMLResponse)
def landing() -> HTMLResponse:
    """Statyczna strona startowa z linkami do narzędzi."""
    index_path = STATIC_DIR / "index.html"
    html = index_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/health/storage")
def health_storage() -> dict:
    """Sprawdza możliwość zapisu i odczytu w warstwie storage (SSD)."""
    test_project_id = "healthcheck"
    content = "ok"
    try:
        storage.write_text("ssd", "healthchecks", f"{test_project_id}.txt", content=content)
        read_back = storage.read_text("ssd", "healthchecks", f"{test_project_id}.txt")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Storage error: {exc}") from exc

    if read_back != content:
        raise HTTPException(status_code=500, detail="Storage roundtrip mismatch")

    return {"status": "ok"}


@app.get("/health/celery")
def health_celery() -> dict:
    """Sprawdza komunikację API -> broker Redis -> worker Celery."""
    try:
        # Czy worker żyje (odpowiada na ping)?
        replies = celery_app.control.ping(timeout=1.0)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Celery control error: {exc}") from exc

    if not replies:
        raise HTTPException(status_code=503, detail="No Celery workers responded to ping")

    # Dodatkowo – wrzuć lekkie zadanie bez czekania na wynik (test kolejki/brokera).
    async_result = celery_app.send_task("kombajn.tasks.ping", kwargs={"payload": "ping"})

    return {
        "status": "ok",
        "workers": replies,
        "test_task_id": async_result.id,
    }


@app.get("/health/full")
def health_full() -> dict:
    """Łączny healthcheck: API, storage, Celery/worker."""
    basic = health()
    storage_status = health_storage()
    celery_status = health_celery()
    return {
        "status": "ok",
        "components": {
            "basic": basic,
            "storage": storage_status,
            "celery": celery_status,
        },
    }


@app.post("/tasks/tracer")
def create_tracer_task(project_id: str) -> dict:
    """Tworzy zadanie Celery, które zapisze JSON w storage."""
    async_result = celery_app.send_task("kombajn.tasks.tracer_bullet", kwargs={"project_id": project_id})
    return {"task_id": async_result.id, "project_id": project_id}

