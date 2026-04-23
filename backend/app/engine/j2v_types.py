from typing import List, Optional, Union, Dict, Any, Annotated
from pydantic import BaseModel, Field

from backend.app.schemas.video.j2v_element import J2VElement
from backend.app.schemas.video.image_element import ImageElement
from backend.app.schemas.video.text_element import TextElement
from backend.app.schemas.video.audio_element import AudioElement
from backend.app.schemas.video.video_element import VideoElement
from backend.app.schemas.video.voice_element import VoiceElement
from backend.app.schemas.video.audiogram_element import AudiogramElement
from backend.app.schemas.video.subtitles_element import SubtitlesElement
from backend.app.schemas.video.component_element import ComponentElement

from backend.app.schemas.video.j2v_scene import J2VScene
from backend.app.schemas.video.j2v_movie import J2VMovie

# --- UNION TYPE ---
J2VAnyElement = Annotated[
    Union[
        ImageElement, TextElement, AudioElement, VideoElement, 
        VoiceElement, AudiogramElement, SubtitlesElement, ComponentElement
    ],
    Field(discriminator='type')
]

# Dodajemy J2VAnyElement do J2VScene i J2VMovie poprzez update_forward_refs w Pydantic v1 
# lub po prostu redefiniując je tutaj jeśli chcemy zachować kompatybilność w j2v_types.

class J2VSceneExt(J2VScene):
    elements: List[J2VAnyElement] = Field(default_factory=list)

class J2VMovieExt(J2VMovie):
    scenes: List[J2VSceneExt] = Field(default_factory=list)
    elements: List[J2VAnyElement] = Field(default_factory=list)

# Aliasy dla zachowania kompatybilności wstecznej w silniku
J2VScene = J2VSceneExt
J2VMovie = J2VMovieExt

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
