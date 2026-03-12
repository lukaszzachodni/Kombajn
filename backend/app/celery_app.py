from celery import Celery
import os
from .config import settings
from .router import KombajnRouter

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

# Dynamic Routing
celery_app.conf.task_default_queue = 'q_default'
celery_app.conf.task_routes = (KombajnRouter(),)

celery_app.autodiscover_tasks(["backend.app"])
