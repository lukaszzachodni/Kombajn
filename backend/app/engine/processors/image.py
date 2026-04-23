from moviepy.editor import ImageClip, vfx
from backend.app.schemas.video.image_element import ImageElement
from ..j2v_base_processor import J2VBaseProcessor

class J2VImageProcessor:
    def process(self, width: int, height: int, element_data: dict, container_duration: float):
        el = ImageElement(**element_data)
        clip = ImageClip(el.src)
        if el.resize == "cover":
            clip = clip.resize(width=width) if (width/height > clip.w/clip.h) else clip.resize(height=height)
        elif el.resize == "fit":
            clip = clip.resize(width=width) if (width/height < clip.w/clip.h) else clip.resize(height=height)
        pos_map = {"top-left": (0.05*width, 0.05*height), "center-center": ("center", "center")}
        clip = clip.set_position(pos_map.get(el.position, (el.x, el.y)))
        return J2VBaseProcessor.apply_common_properties(clip, el, container_duration)
