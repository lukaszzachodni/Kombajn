from fastapi import APIRouter
from ...celery_app import celery_app

router = APIRouter()

@router.get("/list")
def list_tasks():
    i = celery_app.control.inspect()
    active = i.active() or {}
    reserved = i.reserved() or {}
    
    tasks_list = []
    for worker_data in [active, reserved]:
        for worker, tasks in worker_data.items():
            for t in tasks:
                kwargs = t.get('kwargs', {})
                tasks_list.append({
                    "task_id": t.get('id'),
                    "project_name": kwargs.get('project_name', 'N/A'),
                    "status": "ACTIVE" if worker_data == active else "RESERVED",
                    "timestamp": t.get('time_start', 'N/A')
                })
    return {"tasks": tasks_list}
