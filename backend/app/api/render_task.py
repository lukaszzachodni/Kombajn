from fastapi import APIRouter
from backend.app.celery_app import celery_app
from backend.app.engine.j2v_types import J2VMovie

router = APIRouter()

@router.post("/j2v-render")
def create_j2v_render_task(manifest: J2VMovie):
    async_result = celery_app.send_task(
        "kombajn.tasks.orchestrate_video_render",
        kwargs={"manifest_dict": manifest.model_dump(by_alias=True)},
    )
    return {"task_id": async_result.id}
