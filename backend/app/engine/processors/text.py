from moviepy.editor import TextClip
from backend.app.schemas.video.text_element import TextElement
from ..j2v_base_processor import J2VBaseProcessor

class J2VTextProcessor:
    def process(self, width: int, height: int, element_data: dict, container_duration: float):
        el = TextElement(**element_data)
        settings = el.settings
        duration = el.duration if el.duration > 0 else container_duration
        txt_clip = TextClip(
            el.text,
            fontsize=int(settings.get("font-size", 70)),
            color=settings.get("font-color", "white"),
            font="Arial",
            method="caption",
            size=(width, None)
        ).set_duration(duration)
        if txt_clip.ismask: txt_clip = txt_clip.to_RGB()
        v_pos = settings.get("vertical-position", "center")
        h_pos = settings.get("horizontal-position", "center")
        txt_clip = txt_clip.set_position((h_pos, v_pos)).set_start(el.start)
        return J2VBaseProcessor.apply_common_properties(txt_clip, el, container_duration)
