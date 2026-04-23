from typing import Optional, Literal
from pydantic import Field
from .j2v_element import J2VElement
from backend.app.schemas.common.types import HInt, HFloat, HBool

class AudioElement(J2VElement):
    type: Literal["audio"] = "audio"
    src: str = Field(..., description="URL to audio file (MP3/WAV)")
    
    # Hybrid fields for templates
    volume: HFloat = Field(1.0, description="Volume (0.0 to 10.0)")
    muted: HBool = False
    loop: HInt = Field(1, description="Loop count (-1 = infinite)")
    seek: HFloat = Field(0.0, description="Audio start offset")
