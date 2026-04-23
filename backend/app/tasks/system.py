from backend.app.celery_app import celery_app

@celery_app.task(name="kombajn.tasks.ping", bind=True)
def ping(self) -> dict:
    return {"echo": "ping", "worker": self.request.hostname}
