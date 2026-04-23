from typing import Optional, Literal
from pydantic import Field
from .j2v_element import J2VElement
from .subtitles_settings import SubtitlesSettings

class SubtitlesElement(J2VElement):
    type: Literal["subtitles"] = "subtitles"
    captions: Optional[str] = Field(None, description="URL to SRT/VTT file or inline text")
    language: str = "auto"
    model: str = "default"
    settings: SubtitlesSettings = SubtitlesSettings()
