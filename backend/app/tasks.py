from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import os
import shutil
import logging

from celery import chord
from .celery_app import celery_app
from .engine.j2v_renderer import J2VMovieRenderer
from .engine.j2v_types import J2VMovie
from moviepy.editor import VideoFileClip, concatenate_videoclips

logger = logging.getLogger(__name__)

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
    logger.info(f"Created temp root: {temp_root}")

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
        "scene_count": len(header_tasks),
        "temp_root": str(temp_root)
    }

@celery_app.task(name="kombajn.tasks.render_scene", bind=True)
def render_scene_task(self, render_id: str, scene_index: int, scene_dict: dict, movie_config: dict) -> dict:
    """
    Stage 3: Parallel Scene Rendering
    Atomic unit of work for a single scene.
    """
    temp_dir = Path("/data/ssd/temp") / render_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock manifest for renderer (single scene)
    pseudo_manifest = {
        "width": movie_config["width"],
        "height": movie_config["height"],
        "fps": movie_config["fps"],
        "variables": movie_config["variables"],
        "scenes": [scene_dict]
    }
    
    # Use J2VMovieRenderer with specific temp_dir
    renderer = J2VMovieRenderer(pseudo_manifest, temp_dir=temp_dir)
    
    # Render the scene
    paths = renderer.render_scene(scene_dict, scene_index, movie_config["variables"])
    
    # Verify file existence before returning
    for p in paths:
        if not Path(p).exists():
            raise FileNotFoundError(f"Scene file not found after rendering: {p}")
    
    return {
        "status": "completed",
        "render_id": render_id,
        "scene_index": scene_index,
        "rendered_paths": paths,
        "worker": self.request.hostname,
        "video_codec": renderer.video_codec
    }

@celery_app.task(name="kombajn.tasks.assemble_video", bind=True)
def assemble_video_task(self, results: List[dict], render_id: str, output_path: str) -> dict:
    """
    Stage 5: Assembly (Stitching)
    Concatenates all intermediate files in order.
    """
    logger.info(f"Assembling video for render_id: {render_id}")
    
    # Sort results by scene_index to ensure correct order
    sorted_results = sorted(results, key=lambda x: x['scene_index'])
    
    all_clips = []
    try:
        for res in sorted_results:
            for path in res['rendered_paths']:
                p = Path(path)
                if not p.exists():
                    logger.error(f"CRITICAL: Missing scene file at {path} (Worker reported: {res['worker']})")
                    raise FileNotFoundError(f"Missing scene file: {path}")
                all_clips.append(VideoFileClip(str(p)))
        
        if not all_clips:
            return {"status": "failed", "error": "No clips to assemble"}

        final_video = concatenate_videoclips(all_clips, method="compose")
        
        # Detect codec for final assembly
        dummy_renderer = J2VMovieRenderer({"width": 1920, "height": 1080, "fps": 24, "scenes": []})
        
        final_video.write_videofile(
            output_path, 
            fps=all_clips[0].fps, 
            codec=dummy_renderer.video_codec, 
            audio_codec="aac"
        )
        
        return {
            "status": "completed",
            "output_path": output_path,
            "render_id": render_id,
            "video_codec": dummy_renderer.video_codec
        }

    except Exception as e:
        logger.error(f"Assembly failed: {e}")
        raise e
    finally:
        # Cleanup
        for clip in all_clips:
            try: clip.close()
            except: pass
        
        # Cleanup temp directory if assembly was successful
        temp_dir = Path("/data/ssd/temp") / render_id
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Failed to cleanup temp directory {temp_dir}: {e}")

@celery_app.task(name="kombajn.tasks.ping", bind=True)
def ping(self) -> dict:
    return {"echo": "ping", "worker": self.request.hostname}
