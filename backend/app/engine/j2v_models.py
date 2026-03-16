from typing import List, Optional, Union, Dict, Any, Literal, Tuple
from pydantic import BaseModel, Field, field_validator
from .j2v_types import J2VElement

# --- STATIC ELEMENTS MODELS ---

class RotateSettings(BaseModel):
    angle: float = 0.0
    speed: float = 0.0

class CropSettings(BaseModel):
    width: int
    height: int
    x: int = 0
    y: int = 0

class CorrectionSettings(BaseModel):
    brightness: float = 0.0
    contrast: float = 1.0
    gamma: float = 1.0
    saturation: float = 1.0

class ImageElement(J2VElement):
    type: Literal["image"] = "image"
    src: Optional[str] = None
    
    # AI Generation
    prompt: Optional[str] = None
    model: Optional[str] = None
    aspect_ratio: str = Field("horizontal", alias="aspect-ratio")
    
    # Transformation
    width: int = -1
    height: int = -1
    x: int = 0
    y: int = 0
    position: str = "custom"
    resize: Optional[Literal["cover", "fill", "fit", "contain"]] = None
    rotate: Optional[Union[float, RotateSettings]] = None
    crop: Optional[CropSettings] = None
    
    # Effects
    zoom: int = Field(0, ge=-10, le=10)
    pan: Optional[Literal["left", "top", "right", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"]] = None
    
    correction: Optional[CorrectionSettings] = None

class TextElement(J2VElement):
    type: Literal["text"] = "text"
    text: str
    style: str = "001"
    settings: Dict[str, Any] = {} # CSS-like settings
    
    # Transformation
    width: int = -1
    height: int = -1
    x: int = 0
    y: int = 0
    position: str = "custom"
    rotate: Optional[Union[float, RotateSettings]] = None

class AudioElement(J2VElement):
    type: Literal["audio"] = "audio"
    src: str
    
    # Audio specific
    volume: float = 1.0
    muted: bool = False
    loop: int = 1 # 1: once, -1: forever
    seek: float = 0.0

class VideoElement(J2VElement):
    type: Literal["video"] = "video"
    src: str
    
    # Transformation
    width: int = -1
    height: int = -1
    x: int = 0
    y: int = 0
    position: str = "custom"
    resize: Optional[Literal["cover", "fill", "fit", "contain"]] = None
    rotate: Optional[Union[float, RotateSettings]] = None
    crop: Optional[CropSettings] = None
    flip_horizontal: bool = Field(False, alias="flip-horizontal")
    flip_vertical: bool = Field(False, alias="flip-vertical")
    
    # Audio aspect of video
    volume: float = 1.0
    muted: bool = False
    loop: int = 1
    seek: float = 0.0
    
    # Effects
    zoom: int = Field(0, ge=-10, le=10)
    pan: Optional[Literal["left", "top", "right", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"]] = None
    correction: Optional[CorrectionSettings] = None

class VoiceElement(J2VElement):
    type: Literal["voice"] = "voice"
    text: str
    voice: Optional[str] = None
    model: str = "azure" # We will use edge-tts to simulate azure/elevenlabs locally
    volume: float = 1.0
    muted: bool = False

class AudiogramElement(J2VElement):
    type: Literal["audiogram"] = "audiogram"
    color: str = "#ffffff"
    amplitude: float = 5.0
    opacity: float = 0.5
    # Transformation
    width: int = -1
    height: int = -1
    x: int = 0
    y: int = 0
    position: str = "custom"

class SubtitlesSettings(BaseModel):
    font_family: str = Field("Arial", alias="font-family")
    font_size: Optional[int] = Field(None, alias="font-size")
    font_color: str = Field("#ffffff", alias="font-color")
    style: str = "classic"
    position: str = "bottom-center"

class SubtitlesElement(J2VElement):
    type: Literal["subtitles"] = "subtitles"
    captions: Optional[str] = None # URL or inline string
    language: str = "auto"
    model: str = "default" # We'll use Whisper locally
    settings: SubtitlesSettings = SubtitlesSettings()

# Registry for Pydantic to know which model to use
ELEMENT_MODEL_MAP = {
    "image": ImageElement,
    "text": TextElement,
    "audio": AudioElement,
    "video": VideoElement,
    "voice": VoiceElement,
    "audiogram": AudiogramElement,
    "subtitles": SubtitlesElement
}
