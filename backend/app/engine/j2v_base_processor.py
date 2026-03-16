from typing import Any
from moviepy.editor import vfx
from moviepy.Clip import Clip

class J2VBaseProcessor:
    """
    Base logic for applying J2V common properties to MoviePy clips.
    SRP: Responsibility is ONLY to apply common metadata (timing, fades, z-index).
    """
    
    @staticmethod
    def apply_common_properties(clip: Clip, element: Any, container_duration: float) -> Clip:
        """
        Processes common J2V fields: start, duration, extra-time, fades.
        """
        # 1. Resolve Duration
        # duration: -1 (asset length), -2 (container length)
        final_duration = getattr(element, "duration", -2.0)
        
        # Determine asset's own duration if available
        asset_duration = clip.duration if (hasattr(clip, "duration") and clip.duration) else None
        
        if final_duration == -2:
            final_duration = container_duration
        elif final_duration == -1:
            if asset_duration:
                final_duration = asset_duration
            else:
                final_duration = container_duration
        
        # Apply extra-time
        final_duration += getattr(element, "extra_time", 0.0)
        
        # SAFETY: Never exceed container if start + duration > container
        # But for global elements we might allow it. 
        # For now, let's just set the resolved duration.
        clip = clip.set_duration(final_duration).set_start(element.start)
        
        # 2. Apply Fades
        if getattr(element, "fade_in", None):
            clip = clip.fadein(element.fade_in)
        if getattr(element, "fade_out", None):
            clip = clip.fadeout(element.fade_out)
            
        # 3. Set Metadata for Layering
        clip.z_index = getattr(element, "z_index", 0)
        
        return clip
