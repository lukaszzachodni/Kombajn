from typing import Optional, Literal, Union
from pydantic import Field
from .j2v_element import J2VElement
from backend.app.schemas.common.types import HInt, HFloat, HBool
from .rotate_settings import RotateSettings
from .crop_settings import CropSettings
from .correction_settings import CorrectionSettings

class VideoElement(J2VElement):
    type: Literal["video"] = "video"
    src: str = Field(..., description="URL to video file")
    
    # Hybrid fields for templates
    width: HInt = Field(-1, description="Video width")
    height: HInt = Field(-1, description="Video height")
    x: HInt = Field(0, description="X coordinate")
    y: HInt = Field(0, description="Y coordinate")
    
    position: str = "custom"
    resize: Optional[Union[Literal["cover", "fill", "fit", "contain"], str]] = None
    rotate: Optional[Union[HFloat, RotateSettings]] = None
    crop: Optional[CropSettings] = None
    
    # Audio settings (Hybrid)
    volume: HFloat = 1.0
    muted: HBool = False
    loop: HInt = 1
    seek: HFloat = 0.0
    
    correction: Optional[CorrectionSettings] = None
