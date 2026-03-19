from fastapi import APIRouter
from ..celery_app import celery_app

router = APIRouter()

@router.get("/health/full")
def health_full():
    replies = celery_app.control.ping(timeout=1.0)
    return {"status": "ok", "workers": replies}
