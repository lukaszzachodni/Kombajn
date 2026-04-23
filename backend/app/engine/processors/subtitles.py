from moviepy.editor import TextClip
from backend.app.schemas.video.subtitles_element import SubtitlesElement
from ..j2v_base_processor import J2VBaseProcessor

class J2VSubtitlesProcessor:
    def process(self, width: int, height: int, element_data: dict, container_duration: float):
        el = SubtitlesElement(**element_data)
        txt = TextClip("Subtitles Placeholder", fontsize=40, color='yellow').set_position(("center", "bottom"))
        return J2VBaseProcessor.apply_common_properties(txt, el, container_duration)
