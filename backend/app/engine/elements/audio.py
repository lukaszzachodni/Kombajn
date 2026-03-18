from typing import Optional, Literal
from pydantic import Field
from .base import J2VElement

class AudioElement(J2VElement):
    type: Literal["audio"] = "audio"
    src: str = Field(..., description="URL to audio file (MP3/WAV)")
    volume: float = Field(1.0, description="Volume (0.0 to 10.0)")
    muted: bool = False
    loop: int = Field(1, description="Loop count (-1 = infinite)")
    seek: float = Field(0.0, description="Audio start offset")
