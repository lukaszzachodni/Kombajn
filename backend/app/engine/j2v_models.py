from .j2v_types import (
    ImageElement, TextElement, AudioElement, VideoElement, 
    VoiceElement, AudiogramElement, SubtitlesElement, ComponentElement,
    J2VAnyElement
)

# Registry for Pydantic or UI Factory to know which model to use
ELEMENT_MODEL_MAP = {
    "image": ImageElement,
    "text": TextElement,
    "audio": AudioElement,
    "video": VideoElement,
    "voice": VoiceElement,
    "audiogram": AudiogramElement,
    "subtitles": SubtitlesElement,
    "component": ComponentElement
}
