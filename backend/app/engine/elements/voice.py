from typing import Optional, Literal
from pydantic import Field
from .base import J2VElement, HInt, HFloat, HBool

class VoiceElement(J2VElement):
    type: Literal["voice"] = "voice"
    text: str = Field(..., description="Text to be spoken by AI")
    voice: Optional[str] = Field(None, description="Voice ID (e.g. en-US-AriaNeural)")
    model: str = Field("azure", description="TTS model provider")
    
    # Hybrid settings
    volume: HFloat = 1.0
    muted: HBool = False
    connection: Optional[str] = None
