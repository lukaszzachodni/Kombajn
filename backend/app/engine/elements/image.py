from typing import Any, Dict, Optional, Union, Literal
from pydantic import BaseModel, Field
from .base import J2VElement
from .settings import RotateSettings, CropSettings, CorrectionSettings

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
