from pathlib import Path
from typing import List
from PIL import Image
# Monkey-patch for MoviePy compatibility with Pillow 10+
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

from moviepy.editor import CompositeVideoClip
from moviepy.Clip import Clip
from ..schemas import Scene
from .factory import ProcessorFactory

class SceneRenderer:
    """
    Orchestrates the lifecycle of rendering a single scene.
    Responsibility: Coordinate processors and write final file.
    """
    def __init__(self, project_id: str, width: int, height: int, fps: int):
        self.project_id = project_id
        self.width = width
        self.height = height
        self.fps = fps
        self.temp_dir = Path("/data/ssd/temp") / project_id

    def _prepare_directory(self):
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def render(self, scene: Scene, index: int) -> str:
        """Renders a single scene and returns the path to the temporary .mp4 file."""
        self._prepare_directory()
        output_path = self.temp_dir / f"scene_{index:03d}.mp4"
        
        # 1. Process Background
        bg_proc = ProcessorFactory.get_processor(scene.background.type)
        bg_clip = bg_proc.create_clip(self.width, self.height, context=scene.background)
        
        # 2. Process Elements
        clips: List[Clip] = [bg_clip]
        for element in scene.elements:
            el_proc = ProcessorFactory.get_processor(element.type)
            el_clip = el_proc.create_clip(
                self.width, self.height, context=element, bg_duration=bg_clip.duration
            )
            clips.append(el_clip)

        # 3. Composite and Write
        final_scene = CompositeVideoClip(clips, size=(self.width, self.height))
        final_scene.write_videofile(
            str(output_path), 
            fps=self.fps, 
            codec="libx264", 
            audio=False, 
            logger=None
        )
        
        # 4. Explicit Cleanup
        for clip in clips:
            clip.close()
        
        return str(output_path)
