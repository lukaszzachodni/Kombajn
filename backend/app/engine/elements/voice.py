from typing import Optional, Literal
from pydantic import Field
from .base import J2VElement

class VoiceElement(J2VElement):
    type: Literal["voice"] = "voice"
    text: str = Field(..., description="Text to be spoken by AI")
    voice: Optional[str] = Field(None, description="Voice ID (e.g. en-US-AriaNeural)")
    model: str = Field("azure", description="TTS model provider")
    volume: float = 1.0
    muted: bool = False
    connection: Optional[str] = None
