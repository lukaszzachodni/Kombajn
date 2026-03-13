from datetime import datetime, timezone
from pathlib import Path
from typing import List, Union, Dict, Any
import os

from moviepy.editor import ColorClip, CompositeVideoClip, TextClip, ImageClip, concatenate_videoclips, VideoFileClip

from .celery_app import celery_app
from .schemas import DatetimeToTimestampRequest, DatetimeToTimestampResult, VideoEditManifest, Scene
from .storage import StorageManager

storage = StorageManager()

# Set this to True in environment to skip actual rendering and just log plans
DRY_RUN = os.getenv("KOMBAJN_DRY_RUN", "true").lower() == "true"

@celery_app.task(name="kombajn.tasks.render_scene", bind=True)
def render_scene(self, project_id: str, scene_dict: dict, width: int, height: int, fps: int, scene_index: int) -> dict:
    worker_name = self.request.hostname
    scene = Scene(**scene_dict)
    
    print(f"✅ [FACTORY REACHED] Scene {scene_index} for project {project_id}")
    
    # 📝 LOGGING THE "PLAN"
    bg = scene.background
    print(f"   🖼️ BACKGROUND: type={bg.type}, duration={getattr(bg, 'duration', 'N/A')}s")
    
    for i, el in enumerate(scene.elements):
        if el.type == "text":
            print(f"   🔤 ELEMENT {i}: Adding text '{el.text}' at position {el.position} (starts at {el.start_time}s)")

    if DRY_RUN:
        print(f"   ⏩ [DRY RUN] Skipping actual MoviePy render for scene {scene_index}")
        # Create a fake path for the flow to continue
        temp_path = f"/data/ssd/temp/{project_id}/fake_scene_{scene_index}.mp4"
        return {"path": temp_path, "worker": worker_name, "dry_run": True}

    # --- ACTUAL RENDERING LOGIC ---
    temp_dir = Path("/data/ssd") / "temp" / project_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"scene_{scene_index:03d}.mp4"

    if bg.type == "color":
        bg_clip = ColorClip(size=(width, height), color=bg.color, duration=bg.duration)
    elif bg.type == "image":
        bg_clip = ImageClip(bg.path).set_duration(bg.duration)
        bg_clip = bg_clip.resize(height=height)
    else:
        bg_clip = ColorClip(size=(width, height), color="black", duration=5.0)

    element_clips = [bg_clip]
    for el in scene.elements:
        if el.type == "text":
            txt = TextClip(el.text, fontsize=el.fontsize, color=el.color, font="DejaVu-Sans", method="label")
            txt = txt.set_start(el.start_time).set_duration(el.duration or bg_clip.duration).set_position(el.position)
            element_clips.append(txt)

    final_scene = CompositeVideoClip(element_clips, size=(width, height))
    final_scene.write_videofile(str(temp_path), fps=fps, codec="libx264", audio=False, logger=None)
    
    return {"path": str(temp_path), "worker": worker_name, "dry_run": False}


@celery_app.task(name="kombajn.tasks.assemble_video", bind=True)
def assemble_video(self, scene_results: List[Dict[str, Any]], project_id: str, fps: int) -> dict:
    worker_name = self.request.hostname
    print(f"✅ [FACTORY REACHED] Assembly for project {project_id}")
    
    scene_paths = [res["path"] for res in scene_results]
    is_dry_run = any(res.get("dry_run", False) for res in scene_results)

    if DRY_RUN or is_dry_run:
        print(f"   🎞️ [DRY RUN] Would concatenate {len(scene_paths)} scenes into the final movie.")
        output_path = f"/data/ssd/renders/{project_id}/fake_final.mp4"
        return {"project_id": project_id, "final_path": output_path, "status": "dry_run_completed", "worker": worker_name}

    # --- ACTUAL ASSEMBLY ---
    output_dir = Path("/data/ssd") / "renders" / project_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    video_clips = [VideoFileClip(p) for p in scene_paths]
    final_clip = concatenate_videoclips(video_clips, method="compose")
    final_clip.write_videofile(str(output_path), fps=fps, codec="libx264", audio=False, logger=None)

    for p in scene_paths:
        try: Path(p).unlink()
        except: pass

    print(f"📽️ [FINISHED MOVIE] Movie for project {project_id} is READY at {output_path}")
    return {"project_id": project_id, "final_path": str(output_path), "status": "completed", "worker": worker_name}


@celery_app.task(name="kombajn.tasks.orchestrate_video_render")
def orchestrate_video_render(manifest_dict: dict):
    manifest = VideoEditManifest(**manifest_dict)
    header = [
        celery_app.signature("kombajn.tasks.render_scene", args=(manifest.project_id, scene.model_dump(), manifest.width, manifest.height, manifest.fps, i))
        for i, scene in enumerate(manifest.scenes)
    ]
    callback = celery_app.signature("kombajn.tasks.assemble_video", kwargs={"project_id": manifest.project_id, "fps": manifest.fps})
    from celery import chord
    chord(header)(callback)
    return {"status": "orchestration_started", "scene_count": len(manifest.scenes)}


@celery_app.task(name="kombajn.tasks.ping", bind=True)
def ping(self) -> dict:
    return {"echo": "ping", "worker": self.request.hostname}
