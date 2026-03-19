from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import os

from moviepy.editor import concatenate_videoclips, VideoFileClip

from .celery_app import celery_app
from .engine.j2v_renderer import J2VMovieRenderer

@celery_app.task(name="kombajn.tasks.j2v_render_movie")
def j2v_render_movie(manifest_dict: dict) -> dict:
    """Task to render a video using the J2V Local Clone renderer."""
    render_id = f"j2v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = Path("/data/ssd/renders")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{render_id}.mp4"
    
    renderer = J2VMovieRenderer(manifest_dict)
    renderer.render_full_movie(str(output_path))
    
    return {
        "status": "completed",
        "output_path": str(output_path),
        "render_id": render_id
    }

@celery_app.task(name="kombajn.tasks.ping", bind=True)
def ping(self) -> dict:
    return {"echo": "ping", "worker": self.request.hostname}
