from typing import List, Optional, Union, Dict, Any, Literal, TYPE_CHECKING, Tuple, Annotated
from pydantic import BaseModel, Field, FieldValidationInfo, field_validator

# --- 1. SHARED SETTINGS ---

class ChromaKeySettings(BaseModel):
    model_config = {"populate_by_name": True}
    color: str = Field(..., description="Color to remove (e.g. #00b140 for green screen)")
    tolerance: int = Field(25, description="Chroma key sensitivity (1-100)")

class RotateSettings(BaseModel):
    model_config = {"populate_by_name": True}
    angle: float = Field(0.0, description="Rotation angle in degrees")
    speed: float = Field(0.0, description="Rotation speed for animation")

class CropSettings(BaseModel):
    model_config = {"populate_by_name": True}
    width: int = Field(..., description="Crop width")
    height: int = Field(..., description="Crop height")
    x: int = Field(0, description="Crop X start point")
    y: int = Field(0, description="Crop Y start point")

class CorrectionSettings(BaseModel):
    model_config = {"populate_by_name": True}
    brightness: float = Field(0.0, description="Brightness (-1.0 to 1.0)")
    contrast: float = Field(1.0, description="Contrast multiplier")
    gamma: float = Field(1.0, description="Gamma correction")
    saturation: float = Field(1.0, description="Saturation multiplier")

# --- 2. BASE ELEMENT ---

class J2VElement(BaseModel):
    """Common properties for all JSON2Video elements."""
    model_config = {
        "protected_namespaces": (),
        "populate_by_name": True
    }
    
    type: str = Field(..., description="Element type")
    id: Optional[str] = Field(None, description="Unique element ID")
    comment: Optional[str] = Field(None, description="Internal notes (not rendered)")
    condition: Optional[Union[str, bool]] = Field(None, description="Expression to decide if element is rendered")
    variables: Optional[Dict[str, Any]] = Field(None, description="Local variables for this element")
    
    # Timing
    start: float = Field(0.0, description="Start time in seconds")
    duration: float = Field(-2.0, description="Duration in seconds (-1: auto asset, -2: auto container)")
    extra_time: float = Field(0.0, alias="extra-time", description="Additional time after completion")
    
    # Visuals
    z_index: int = Field(0, alias="z-index", description="Stacking order (higher is on top)")
    fade_in: Optional[float] = Field(None, alias="fade-in", description="Fade-in duration")
    fade_out: Optional[float] = Field(None, alias="fade-out", description="Fade-out duration")
    mask: Optional[str] = Field(None, description="URL to mask file (PNG/Video)")
    chroma_key: Optional[ChromaKeySettings] = Field(None, alias="chroma-key")
    
    # Common Transformation
    flip_horizontal: bool = Field(False, alias="flip-horizontal", description="Flip horizontally")
    flip_vertical: bool = Field(False, alias="flip-vertical", description="Flip vertically")
    zoom: int = Field(0, ge=-10, le=10, description="Zoom level (-10 to 10)")
    pan: Optional[Literal["left", "top", "right", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"]] = Field(None, description="Panning direction")
    pan_crop: bool = Field(True, alias="pan-crop", description="Fill screen during panning")
    pan_distance: float = Field(0.1, alias="pan-distance", description="Panning distance")

    cache: bool = Field(True, description="Enable/disable caching for this element")

# --- 3. CONCRETE ELEMENTS ---

class ImageElement(J2VElement):
    type: Literal["image"] = "image"
    src: Optional[str] = Field(None, description="URL to image (JPG/PNG/GIF)")
    prompt: Optional[str] = Field(None, description="AI image generation prompt")
    model: Optional[str] = Field(None, description="AI model (e.g. flux-pro)")
    model_settings: Optional[Dict[str, Any]] = Field(None, alias="model-settings")
    aspect_ratio: str = Field("horizontal", alias="aspect-ratio")
    connection: Optional[str] = Field(None, description="Connection ID for AI provider")
    width: int = -1
    height: int = -1
    x: int = 0
    y: int = 0
    position: str = Field("custom", description="Predefined position or 'custom'")
    resize: Optional[Literal["cover", "fill", "fit", "contain"]] = None
    rotate: Optional[Union[float, RotateSettings]] = None
    crop: Optional[CropSettings] = None
    correction: Optional[CorrectionSettings] = None

class TextElement(J2VElement):
    type: Literal["text"] = "text"
    text: str = Field(..., description="Text content")
    style: str = Field("001", description="Text animation style ID")
    settings: Dict[str, Any] = Field(default_factory=dict, description="CSS-like text settings")
    width: int = -1
    height: int = -1
    x: int = 0
    y: int = 0
    position: str = "custom"
    rotate: Optional[Union[float, RotateSettings]] = None

class AudioElement(J2VElement):
    type: Literal["audio"] = "audio"
    src: str = Field(..., description="URL to audio file (MP3/WAV)")
    volume: float = Field(1.0, description="Volume (0.0 to 10.0)")
    muted: bool = False
    loop: int = Field(1, description="Loop count (-1 for infinite)")
    seek: float = Field(0.0, description="Audio start offset")

class VideoElement(J2VElement):
    type: Literal["video"] = "video"
    src: str = Field(..., description="URL to video file")
    connection: Optional[str] = None
    width: int = -1
    height: int = -1
    x: int = 0
    y: int = 0
    position: str = "custom"
    resize: Optional[Literal["cover", "fill", "fit", "contain"]] = None
    rotate: Optional[Union[float, RotateSettings]] = None
    crop: Optional[CropSettings] = None
    volume: float = 1.0
    muted: bool = False
    loop: int = 1
    seek: float = 0.0
    correction: Optional[CorrectionSettings] = None

class ComponentElement(J2VElement):
    type: Literal["component"] = "component"
    component: str = Field(..., description="Library component ID")
    settings: Dict[str, Any] = Field(default_factory=dict)
    width: int = -1
    height: int = -1
    x: int = 0
    y: int = 0
    position: str = "custom"
    rotate: Optional[Union[float, RotateSettings]] = None
    resize: Optional[Literal["cover", "fill", "fit", "contain"]] = None
    crop: Optional[CropSettings] = None
    correction: Optional[CorrectionSettings] = None

class VoiceElement(J2VElement):
    type: Literal["voice"] = "voice"
    text: str = Field(..., description="Text to be spoken by AI")
    voice: Optional[str] = Field(None, description="Voice ID (e.g. en-US-AriaNeural)")
    model: str = Field("azure", description="TTS model provider")
    volume: float = 1.0
    muted: bool = False
    connection: Optional[str] = None

class AudiogramElement(J2VElement):
    type: Literal["audiogram"] = "audiogram"
    color: str = Field("#ffffff", description="Waveform color")
    amplitude: float = Field(5.0, description="Waveform amplitude")
    opacity: float = 0.5
    width: int = -1
    height: int = -1
    x: int = 0
    y: int = 0
    position: str = "custom"
    rotate: Optional[Union[float, RotateSettings]] = None
    resize: Optional[Literal["cover", "fill", "fit", "contain"]] = None
    crop: Optional[CropSettings] = None
    correction: Optional[CorrectionSettings] = None

class SubtitlesSettings(BaseModel):
    model_config = {"populate_by_name": True}
    style: str = "classic"
    font_family: str = Field("Arial", alias="font-family")
    font_size: Optional[int] = Field(None, alias="font-size")
    font_color: str = Field("#ffffff", alias="font-color")
    font_url: Optional[str] = Field(None, alias="font-url")
    font_weight: str = Field("400", alias="font-weight")
    all_caps: bool = Field(False, alias="all-caps")
    max_words_per_line: int = Field(4, alias="max-words-per-line")
    box_color: str = Field("#000000", alias="box-color")
    word_color: str = Field("#FFFF00", alias="word-color")
    line_color: str = Field("#FFFFFF", alias="line-color")
    outline_color: str = Field("#000000", alias="outline-color")
    outline_width: int = Field(0, alias="outline-width")
    shadow_color: str = Field("#000000", alias="shadow-color")
    shadow_offset: int = Field(0, alias="shadow-offset")
    position: str = "bottom-center"
    x: int = 0
    y: int = 0
    keywords: Optional[List[str]] = None
    replace: Optional[Dict[str, str]] = None

class SubtitlesElement(J2VElement):
    type: Literal["subtitles"] = "subtitles"
    captions: Optional[str] = Field(None, description="URL to SRT/VTT file or inline text")
    language: str = "auto"
    model: str = "default"
    settings: SubtitlesSettings = SubtitlesSettings()

# --- 4. THE UNION TYPE (Discriminated) ---

J2VAnyElement = Annotated[
    Union[
        ImageElement, TextElement, AudioElement, VideoElement, 
        VoiceElement, AudiogramElement, SubtitlesElement, ComponentElement
    ],
    Field(discriminator='type')
]

# --- 5. CONTAINER OBJECTS ---

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

# --- 6. REBUILD ---
J2VScene.model_rebuild()
J2VMovie.model_rebuild()
