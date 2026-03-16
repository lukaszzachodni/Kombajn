from typing import Any, Tuple
import numpy as np
from moviepy.editor import ColorClip, TextClip, ImageClip
from moviepy.Clip import Clip
from .base import ClipProcessor

def _parse_color(color: Any) -> Tuple[int, int, int]:
    """Ensures color is a valid RGB tuple for MoviePy/Numpy."""
    if isinstance(color, str):
        # MoviePy's ColorClip sometimes struggles with string names in CompositeVideoClip
        # Mapping common names or just using a safe default. 
        # For full stability, we should use a library like webcolors, 
        # but for TDD we will force RGB logic.
        color_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "purple": (128, 0, 128)
        }
        return color_map.get(color.lower(), (0, 0, 0))
    return tuple(color)

class ColorProcessor(ClipProcessor):
    def create_clip(self, width: int, height: int, context: Any, **kwargs) -> Clip:
        rgb = _parse_color(context.color)
        # Force 3-channel RGB array creation
        return ColorClip(size=(width, height), color=rgb, duration=context.duration)

class ImageProcessor(ClipProcessor):
    def create_clip(self, width: int, height: int, context: Any, **kwargs) -> Clip:
        clip = ImageClip(context.path).set_duration(context.duration)
        return clip.resize(height=height)

class TextProcessor(ClipProcessor):
    def create_clip(self, width: int, height: int, context: Any, **kwargs) -> Clip:
        bg_duration = kwargs.get("bg_duration", 5.0)
        duration = context.duration or bg_duration
        
        # 1. Create text as a mask (label)
        txt = TextClip(
            context.text,
            fontsize=context.fontsize,
            color=context.color,
            font=context.font,
            method="label"
        ).set_duration(duration).set_start(context.start_time)
        
        # 2. Definitive Fix for Numpy broadcast:
        # Wrap the text clip into a container that matches the project's RGB structure.
        # .on_color creates a new RGB clip with the text blitted on it.
        return (txt.on_color(
                    size=(width, height), 
                    color=(0,0,0), 
                    pos=context.position, 
                    col_opacity=0
                )
                .set_duration(duration)
                .set_start(context.start_time))
