from moviepy.editor import AudioFileClip
from ..elements.voice import VoiceElement
from ..j2v_base_processor import J2VBaseProcessor
import uuid
from pathlib import Path
from gtts import gTTS

class J2VVoiceProcessor:
    def process(self, width: int, height: int, element_data: dict, container_duration: float):
        el = VoiceElement(**element_data)
        temp_path = Path("/data/ssd/temp/j2v_tts") / f"tts_{uuid.uuid4()}.mp3"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        lang = el.voice.split("-")[0] if el.voice and "-" in el.voice else "en"
        gTTS(text=el.text, lang=lang).save(str(temp_path))
        audio = AudioFileClip(str(temp_path))
        if el.muted: audio = audio.volumex(0)
        else: audio = audio.volumex(el.volume)
        return J2VBaseProcessor.apply_common_properties(audio, el, container_duration)
