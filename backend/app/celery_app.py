from celery import Celery

from .config import settings


celery_app = Celery(
    "kombajn",
    broker=settings.redis_broker_url,
    backend=settings.redis_result_backend,
)

celery_app.conf.task_routes = {
    "kombajn.tasks.tracer_bullet": {"queue": "tracer"},
}

celery_app.autodiscover_tasks(["backend.app"])

