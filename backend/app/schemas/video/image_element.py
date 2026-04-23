from typing import Any, Dict, Optional, Union, Literal
from pydantic import Field
from .j2v_element import J2VElement
from backend.app.schemas.common.types import HInt, HFloat
from .rotate_settings import RotateSettings
from .crop_settings import CropSettings
from .correction_settings import CorrectionSettings

class ImageElement(J2VElement):
    type: Literal["image"] = "image"
    src: Optional[str] = Field(None, description="URL to image (JPG/PNG/GIF)")
    prompt: Optional[str] = Field(None, description="AI image generation prompt")
    model: Optional[str] = Field(None, description="AI model")
    model_settings: Optional[Dict[str, Any]] = Field(None, alias="model-settings")
    aspect_ratio: str = Field("horizontal", alias="aspect-ratio")
    
    # Dimensions (Hybrid)
    width: HInt = Field(-1, description="Image width")
    height: HInt = Field(-1, description="Image height")
    x: HInt = Field(0, description="X coordinate")
    y: HInt = Field(0, description="Y coordinate")
    
    position: str = Field("custom", description="Predefined position or 'custom'")
    resize: Optional[Union[Literal["cover", "fill", "fit", "contain"], str]] = None
    rotate: Optional[Union[HFloat, RotateSettings]] = None
    crop: Optional[CropSettings] = None
    correction: Optional[CorrectionSettings] = None
