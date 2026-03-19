from fastapi import APIRouter
from ..celery_app import celery_app
from ..engine.j2v_types import J2VMovie

router = APIRouter()

@router.post("/j2v-render")
def create_j2v_render_task(manifest: J2VMovie):
    async_result = celery_app.send_task(
        "kombajn.tasks.j2v_render_movie",
        kwargs={"manifest_dict": manifest.model_dump(by_alias=True)},
    )
    return {"task_id": async_result.id}

@router.get("/")
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
