from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import os
import shutil

from celery import chord
from .celery_app import celery_app
from .engine.j2v_renderer import J2VMovieRenderer
from .engine.j2v_types import J2VMovie
from moviepy.editor import VideoFileClip, concatenate_videoclips

@celery_app.task(name="kombajn.tasks.orchestrate_video_render")
def orchestrate_video_render(manifest_dict: dict) -> dict:
    """
    Stage 2: Orchestration (Fan-Out)
    Parses manifest and creates a Celery Chord for parallel scene rendering.
    """
    render_id = f"j2v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    movie = J2VMovie(**manifest_dict)
    
    # Create temp directory for this render
    temp_root = Path("/data/ssd/temp") / render_id
    temp_root.mkdir(parents=True, exist_ok=True)

    # Define tasks for each scene
    header_tasks = []
    for i, scene in enumerate(movie.scenes):
        scene_dict = scene.model_dump()
        # Route specifically to q_cpu_edit
        header_tasks.append(
            render_scene_task.s(
                render_id=render_id,
                scene_index=i,
                scene_dict=scene_dict,
                movie_config={
                    "width": movie.width,
                    "height": movie.height,
                    "fps": movie.fps,
                    "variables": manifest_dict.get("variables", {})
                }
            )
        )

    # Callback: Assembly (Fan-In)
    output_dir = Path("/data/ssd/renders")
    output_dir.mkdir(parents=True, exist_ok=True)
    final_output = output_dir / f"{render_id}.mp4"

    callback = assemble_video_task.s(render_id=render_id, output_path=str(final_output))
    
    # Execute chord
    result = chord(header_tasks)(callback)
    
    return {
        "status": "orchestrated",
        "render_id": render_id,
        "task_id": result.id,
        "scene_count": len(header_tasks)
    }

@celery_app.task(name="kombajn.tasks.render_scene", bind=True)
def render_scene_task(self, render_id: str, scene_index: int, scene_dict: dict, movie_config: dict) -> dict:
    """
    Stage 3: Parallel Scene Rendering
    Atomic unit of work for a single scene.
    """
    # Use J2VMovieRenderer to render just one scene
    # We mock a full manifest structure for the renderer but only process one scene
    pseudo_manifest = {
        "width": movie_config["width"],
        "height": movie_config["height"],
        "fps": movie_config["fps"],
        "variables": movie_config["variables"],
        "scenes": [scene_dict]
    }
    
    renderer = J2VMovieRenderer(pseudo_manifest)
    # Override temp dir to be specific for this render_id
    renderer.temp_dir = Path("/data/ssd/temp") / render_id
    renderer.temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Render the scene (it will be index 0 in our pseudo_manifest)
    paths = renderer.render_scene(scene_dict, scene_index, movie_config["variables"])
    
    return {
        "status": "completed",
        "render_id": render_id,
        "scene_index": scene_index,
        "rendered_paths": paths,
        "worker": self.request.hostname
    }

@celery_app.task(name="kombajn.tasks.assemble_video")
def assemble_video_task(results: List[dict], render_id: str, output_path: str) -> dict:
    """
    Stage 5: Assembly (Stitching)
    Concatenates all intermediate files in order.
    """
    # Sort results by scene_index to ensure correct order
    sorted_results = sorted(results, key=lambda x: x['scene_index'])
    
    all_clips = []
    for res in sorted_results:
        for path in res['rendered_paths']:
            all_clips.append(VideoFileClip(path))
    
    if not all_clips:
        return {"status": "failed", "error": "No clips to assemble"}

    final_video = concatenate_videoclips(all_clips, method="compose")
    
    # Get codec from one of the renderers (or use default detection)
    # For now, we'll let moviepy handle default or use a dummy renderer to detect
    dummy_renderer = J2VMovieRenderer({"width": 1920, "height": 1080, "fps": 24, "scenes": []})
    
    final_video.write_videofile(
        output_path, 
        fps=all_clips[0].fps, 
        codec=dummy_renderer.video_codec, 
        audio_codec="aac"
    )
    
    # Cleanup
    for clip in all_clips:
        clip.close()
    
    temp_dir = Path("/data/ssd/temp") / render_id
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        
    return {
        "status": "completed",
        "output_path": output_path,
        "render_id": render_id
    }

@celery_app.task(name="kombajn.tasks.ping", bind=True)
def ping(self) -> dict:
    return {"echo": "ping", "worker": self.request.hostname}
