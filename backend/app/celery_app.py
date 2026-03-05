from celery import Celery

from .config import settings


celery_app = Celery(
    "kombajn",
    broker=settings.redis_broker_url,
    backend=settings.redis_result_backend,
)

# Wymuszamy wysyĹ‚anie eventĂłw, ktĂłre Flower przechwytuje
celery_app.conf.worker_send_task_events = True
celery_app.conf.task_send_sent_event = True
celery_app.conf.worker_heartbeat = 10
celery_app.conf.worker_enable_remote_control = True

celery_app.conf.task_routes = {
    "kombajn.tasks.datetime_to_timestamp": {"queue": "tracer"},
    "kombajn.tasks.ping": {"queue": "tracer"},
}

celery_app.autodiscover_tasks(["backend.app"])

