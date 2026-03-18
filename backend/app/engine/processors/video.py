from moviepy.editor import VideoFileClip, vfx
from ..elements.video import VideoElement
from ..j2v_base_processor import J2VBaseProcessor

class J2VVideoProcessor:
    def process(self, width: int, height: int, element_data: dict, container_duration: float):
        el = VideoElement(**element_data)
        clip = VideoFileClip(el.src)
        if el.seek > 0: clip = clip.subclip(el.seek)
        
        # Resizing
        if el.resize == "cover":
            clip = clip.resize(width=width) if (width/height > clip.w/clip.h) else clip.resize(height=height)
        elif el.resize == "fit":
            clip = clip.resize(width=width) if (width/height < clip.w/clip.h) else clip.resize(height=height)
            
        if el.flip_horizontal: clip = clip.fx(vfx.mirror_x)
        if el.flip_vertical: clip = clip.fx(vfx.mirror_y)
        if el.muted: clip = clip.without_audio()
        elif el.volume != 1.0: clip = clip.volumex(el.volume)
        
        pos_map = {"top-left": (0.05*width, 0.05*height), "center-center": ("center", "center")}
        clip = clip.set_position(pos_map.get(el.position, (el.x, el.y)))
        
        duration = el.duration if el.duration > 0 else container_duration
        if el.loop == -1 or el.loop > 1: clip = clip.fx(vfx.loop, duration=duration)
        
        return J2VBaseProcessor.apply_common_properties(clip, el, container_duration)
