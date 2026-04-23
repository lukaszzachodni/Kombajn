from moviepy.editor import ColorClip
from backend.app.schemas.video.audiogram_element import AudiogramElement
from ..j2v_base_processor import J2VBaseProcessor

class J2VAudiogramProcessor:
    def process(self, width: int, height: int, element_data: dict, container_duration: float):
        el = AudiogramElement(**element_data)
        clip = ColorClip(size=(width//2, 100), color=(255,255,255), duration=container_duration).set_opacity(el.opacity).set_position(("center", "bottom"))
        return J2VBaseProcessor.apply_common_properties(clip, el, container_duration)
