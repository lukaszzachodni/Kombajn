from celery import Celery
import os
from .config import settings

celery_app = Celery(
    "kombajn",
    broker=settings.redis_broker_url,
    backend=settings.redis_result_backend,
)

# Force event sending for Flower to track them
celery_app.conf.worker_send_task_events = True
celery_app.conf.task_send_sent_event = True
celery_app.conf.worker_heartbeat = 10
celery_app.conf.worker_enable_remote_control = True

# Routing for atomic tasks
celery_app.conf.task_routes = {
    "kombajn.tasks.datetime_to_timestamp": {"queue": "tracer"},
    "kombajn.tasks.ping": {"queue": "tracer"},
    "kombajn.tasks.render_scene": {"queue": "tracer"},
    "kombajn.tasks.assemble_video": {"queue": "tracer"},
    "kombajn.tasks.orchestrate_video_render": {"queue": "tracer"},
}

celery_app.autodiscover_tasks(["backend.app"])
