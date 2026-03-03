from datetime import datetime, timezone

from .celery_app import celery_app
from .storage import StorageManager


storage = StorageManager()


@celery_app.task(name="kombajn.tasks.tracer_bullet")
def tracer_bullet(project_id: str) -> dict:
    """Minimalne zadanie testowe: zapisuje JSON w /data/ssd."""
    payload = {
        "project_id": project_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "message": "Tracer bullet from Celery worker.",
    }
    storage.write_json("ssd", "tracer-bullets", f"{project_id}.json", data=payload)
    return payload


@celery_app.task(name="kombajn.tasks.ping")
def ping(payload: str = "ping") -> dict:
    """Proste zadanie zdrowotne do testu komunikacji z workerem."""
    return {"echo": payload, "timestamp_utc": datetime.now(timezone.utc).isoformat()}

