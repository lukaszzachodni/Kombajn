from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import os

from moviepy.editor import concatenate_videoclips, VideoFileClip

from .celery_app import celery_app
from .schemas import VideoEditManifest, Scene
from .engine.renderer import SceneRenderer

DRY_RUN = os.getenv("KOMBAJN_DRY_RUN", "false").lower() == "true"

@celery_app.task(name="kombajn.tasks.render_scene", bind=True)
def render_scene(self, project_id: str, scene_dict: dict, width: int, height: int, fps: int, scene_index: int) -> dict:
    """Entrypoint for atomic scene rendering."""
    scene = Scene(**scene_dict)
    
    if DRY_RUN:
        temp_path = f"/data/ssd/temp/{project_id}/fake_scene_{scene_index}.mp4"
        return {"path": temp_path, "worker": self.request.hostname, "dry_run": True}

    renderer = SceneRenderer(project_id, width, height, fps)
    path = renderer.render(scene, scene_index)
    
    return {"path": path, "worker": self.request.hostname, "dry_run": False}


@celery_app.task(name="kombajn.tasks.assemble_video", bind=True)
def assemble_video(self, scene_results: List[Dict[str, Any]], project_id: str, fps: int) -> dict:
    """Entrypoint for final video assembly."""
    scene_paths = [res["path"] for res in scene_results]
    
    if DRY_RUN:
        output_path = f"/data/ssd/renders/{project_id}/fake_final.mp4"
        return {"project_id": project_id, "final_path": output_path, "status": "dry_run", "worker": self.request.hostname}

    output_dir = Path("/data/ssd/renders") / project_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    # Concatenate all scenes
    clips = [VideoFileClip(p) for p in scene_paths]
    final_video = concatenate_videoclips(clips, method="compose")
    final_video.write_videofile(str(output_path), fps=fps, codec="libx264", audio=False, logger=None)

    # Cleanup intermediate files
    for clip in clips:
        clip.close()
    for p in scene_paths:
        try: Path(p).unlink()
        except Exception: pass

    return {
        "project_id": project_id, 
        "final_path": str(output_path), 
        "status": "completed", 
        "worker": self.request.hostname
    }


@celery_app.task(name="kombajn.tasks.orchestrate_video_render")
def orchestrate_video_render(manifest_dict: dict):
    """Orchestrates the Fan-Out/Fan-In rendering process."""
    manifest = VideoEditManifest(**manifest_dict)
    
    # 1. Create render tasks for each scene (Fan-Out)
    header = [
        celery_app.signature("kombajn.tasks.render_scene", args=(
            manifest.project_id, scene.model_dump(), manifest.width, manifest.height, manifest.fps, i
        ))
        for i, scene in enumerate(manifest.scenes)
    ]
    
    # 2. Create assembly task (Fan-In callback)
    callback = celery_app.signature("kombajn.tasks.assemble_video", kwargs={
        "project_id": manifest.project_id, "fps": manifest.fps
    })
    
    from celery import chord
    chord(header)(callback)
    
    return {"status": "orchestration_started", "scene_count": len(manifest.scenes)}


@celery_app.task(name="kombajn.tasks.ping", bind=True)
def ping(self) -> dict:
    return {"echo": "ping", "worker": self.request.hostname}
