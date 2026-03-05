from datetime import datetime, timezone

from .celery_app import celery_app
from .schemas import DatetimeToTimestampRequest, DatetimeToTimestampResult
from .storage import StorageManager


storage = StorageManager()


@celery_app.task(name="kombajn.tasks.datetime_to_timestamp")
def datetime_to_timestamp(datetime_iso: str) -> dict:
    """Przelicza datetime (ISO) na timestamp i zapisuje wynik w /data/ssd."""
    # Walidacja wejścia Pydantic (spójna ze światem HTTP/Streamlit)
    validated = DatetimeToTimestampRequest(datetime_iso=datetime_iso)

    dt = datetime.fromisoformat(validated.datetime_iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ts = dt.timestamp()

    result = DatetimeToTimestampResult(timestamp=ts)

    # Zapisz artefakt do wglądu w storage (SSD)
    filename = f"{int(result.timestamp)}.json"
    storage.write_json("ssd", "datetime-timestamps", filename, data=result.model_dump())

    # Walidacja wyjścia (gdyby logika się kiedyś rozrosła)
    return result.model_dump()


@celery_app.task(name="kombajn.tasks.ping")
def ping(payload: str = "ping") -> dict:
    """Proste zadanie zdrowotne do testu komunikacji z workerem."""
    return {"echo": payload, "timestamp_utc": datetime.now(timezone.utc).isoformat()}

