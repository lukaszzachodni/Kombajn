from .elements.base import J2VElement
from .elements.image import ImageElement
from .elements.text import TextElement
from .elements.audio import AudioElement
from .elements.video import VideoElement
from .elements.voice import VoiceElement
from .elements.audiogram import AudiogramElement
from .elements.subtitles import SubtitlesElement
from .elements.component import ComponentElement
from pydantic import BaseModel, Field, FieldValidationInfo, field_validator
from typing import List, Optional, Union, Dict, Any, Annotated

# --- UNION TYPE ---
J2VAnyElement = Annotated[
    Union[
        ImageElement, TextElement, AudioElement, VideoElement, 
        VoiceElement, AudiogramElement, SubtitlesElement, ComponentElement
    ],
    Field(discriminator='type')
]

# --- CONTAINER OBJECTS ---

class J2VScene(BaseModel):
    model_config = {"populate_by_name": True}
    id: Optional[str] = Field(None, description="Scene identifier")
    comment: Optional[str] = None
    condition: Optional[Union[str, bool]] = None
    variables: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Scene-specific variables")
    iterate: Optional[str] = Field(None, description="Array to iterate over for dynamic scenes")
    background_color: str = Field("#000000", alias="background-color", description="Background color")
    duration: float = Field(-1.0, description="Scene duration (-1 for auto)")
    cache: bool = True
    elements: List[J2VAnyElement] = Field(default_factory=list, description="List of elements in the scene")

class J2VMovie(BaseModel):
    model_config = {"populate_by_name": True}
    width: int = Field(1920, description="Video width")
    height: int = Field(1080, description="Video height")
    fps: int = Field(24, description="Frames per second")
    resolution: Optional[str] = Field(None, description="Resolution alias (e.g. shorts)")
    quality: str = "high"
    draft: bool = False
    variables: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Global movie variables")
    scenes: List[J2VScene] = Field(default_factory=list, description="Movie scenes")
    elements: List[J2VAnyElement] = Field(default_factory=list, description="Global elements (overlaying all scenes)")
    
    @field_validator("resolution")
    @classmethod
    def map_resolution(cls, v: Optional[str], info: FieldValidationInfo) -> Optional[str]:
        return v
