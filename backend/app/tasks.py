from datetime import datetime, timezone
from pathlib import Path
from typing import List

from moviepy.editor import ColorClip, CompositeVideoClip, TextClip, ImageClip, concatenate_videoclips, VideoFileClip

from .celery_app import celery_app
from .schemas import DatetimeToTimestampRequest, DatetimeToTimestampResult, VideoEditManifest, Scene
from .storage import StorageManager


storage = StorageManager()


@celery_app.task(name="kombajn.tasks.render_scene", bind=True)
def render_scene(self, project_id: str, scene_dict: dict, width: int, height: int, fps: int, scene_index: int) -> dict:
    """Renders a single scene to a temporary .mp4 file."""
    worker_name = self.request.hostname
    scene = Scene(**scene_dict)
    
    # Temp directory for partial renders
    temp_dir = Path("/data/ssd") / "temp" / project_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"scene_{scene_index:03d}.mp4"

    # 1. Background
    if scene.background.type == "color":
        bg_clip = ColorClip(size=(width, height), color=scene.background.color, duration=scene.background.duration)
    elif scene.background.type == "image":
        bg_clip = ImageClip(scene.background.path).set_duration(scene.background.duration)
        bg_clip = bg_clip.resize(height=height)
        if bg_clip.w < width:
            bg_clip = bg_clip.resize(width=width)
    else:
        bg_clip = ColorClip(size=(width, height), color="black", duration=5.0)

    # 2. Elements (Text)
    element_clips = [bg_clip]
    for el in scene.elements:
        if el.type == "text":
            # MoviePy uses ImageMagick (convert) for TextClip
            txt = TextClip(
                el.text, 
                fontsize=el.fontsize, 
                color=el.color, 
                font="DejaVu-Sans", 
                method="label"
            ).set_start(el.start_time)
            
            duration = (el.end_time - el.start_time) if el.end_time else (bg_clip.duration - el.start_time)
            txt = txt.set_duration(duration).set_position(el.position)
            element_clips.append(txt)

    # 3. Composite and Write Temp File
    final_scene = CompositeVideoClip(element_clips, size=(width, height))
    final_scene.write_videofile(str(temp_path), fps=fps, codec="libx264", audio=False, logger=None)
    
    return {
        "path": str(temp_path),
        "worker": worker_name
    }


@celery_app.task(name="kombajn.tasks.assemble_video", bind=True)
def assemble_video(self, scene_paths: List[str], project_id: str, fps: int) -> dict:
    """Concatenates all partial scene renders into the final output."""
    worker_name = self.request.hostname
    output_dir = Path("/data/ssd") / "renders" / project_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    video_clips = [VideoFileClip(p) for p in scene_paths]
    
    final_clip = concatenate_videoclips(video_clips, method="compose")
    final_clip.write_videofile(str(output_path), fps=fps, codec="libx264", audio=False, logger=None)

    # Clean up temp files
    for p in scene_paths:
        try:
            Path(p).unlink()
        except:
            pass

    return {
        "project_id": project_id,
        "final_path": str(output_path),
        "status": "completed",
        "worker": worker_name
    }


@celery_app.task(name="kombajn.tasks.orchestrate_video_render")
def orchestrate_video_render(manifest_dict: dict):
    """Orchestrates the rendering process using Celery Chords."""
    manifest = VideoEditManifest(**manifest_dict)
    
    header = [
        celery_app.signature(
            "kombajn.tasks.render_scene",
            args=(manifest.project_id, scene.model_dump(), manifest.width, manifest.height, manifest.fps, i)
        )
        for i, scene in enumerate(manifest.scenes)
    ]
    
    callback = celery_app.signature(
        "kombajn.tasks.assemble_video",
        kwargs={"project_id": manifest.project_id, "fps": manifest.fps}
    )
    
    from celery import chord
    chord(header)(callback)
    
    return {"status": "orchestration_started", "scene_count": len(manifest.scenes)}


@celery_app.task(name="kombajn.tasks.datetime_to_timestamp")
def datetime_to_timestamp(datetime_iso: str) -> dict:
    validated = DatetimeToTimestampRequest(datetime_iso=datetime_iso)
    dt = datetime.fromisoformat(validated.datetime_iso.replace("Z", "+00:00"))
    return {"timestamp": dt.timestamp()}


@celery_app.task(name="kombajn.tasks.ping", bind=True)
def ping(self) -> dict:
    return {
        "echo": "ping", 
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "worker": self.request.hostname
    }
