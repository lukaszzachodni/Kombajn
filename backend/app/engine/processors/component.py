from moviepy.editor import TextClip
from ..elements.component import ComponentElement
from ..j2v_base_processor import J2VBaseProcessor

class J2VComponentProcessor:
    def process(self, width: int, height: int, element_data: dict, container_duration: float):
        el = ComponentElement(**element_data)
        txt = TextClip(f"Component: {el.component}", fontsize=50, color='white', bg_color='blue').set_position("center")
        return J2VBaseProcessor.apply_common_properties(txt, el, container_duration)
