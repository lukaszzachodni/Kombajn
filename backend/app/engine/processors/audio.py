from moviepy.editor import AudioFileClip, afx
from backend.app.schemas.video.audio_element import AudioElement
from ..j2v_base_processor import J2VBaseProcessor

class J2VAudioProcessor:
    def process(self, width: int, height: int, element_data: dict, container_duration: float):
        el = AudioElement(**element_data)
        audio = AudioFileClip(el.src)
        if el.seek > 0: audio = audio.subclip(el.seek)
        
        safe_duration = el.duration if el.duration > 0 else (container_duration if el.duration == -2 else audio.duration)
        if el.loop == -1 or el.loop > 1:
            audio = audio.fx(afx.audio_loop, duration=safe_duration)
        else:
            audio = audio.subclip(0, min(audio.duration, safe_duration))
            
        if el.muted: audio = audio.volumex(0)
        else: audio = audio.volumex(el.volume)
        
        return J2VBaseProcessor.apply_common_properties(audio, el, container_duration)
