from fastapi import APIRouter
from ...celery_app import celery_app
from ...engine.j2v_types import J2VMovie

router = APIRouter()

@router.post("/j2v-render")
def create_j2v_render_task(manifest: J2VMovie, project_name: str = "Unnamed"):
    async_result = celery_app.send_task(
        "kombajn.tasks.j2v_render_movie",
        kwargs={"manifest_dict": manifest.model_dump(by_alias=True), "project_name": project_name},
    )
    return {"task_id": async_result.id}
