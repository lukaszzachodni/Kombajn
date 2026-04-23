from typing import Any, Dict, Optional, Union, Literal
from pydantic import Field
from .j2v_element import J2VElement
from backend.app.schemas.common.types import HInt, HFloat
from .rotate_settings import RotateSettings
from .crop_settings import CropSettings
from .correction_settings import CorrectionSettings

class ComponentElement(J2VElement):
    type: Literal["component"] = "component"
    component: str = Field(..., description="Library component ID")
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    # Hybrid fields for templates
    width: HInt = Field(-1, description="Component width")
    height: HInt = Field(-1, description="Component height")
    x: HInt = Field(0, description="X coordinate")
    y: HInt = Field(0, description="Y coordinate")
    
    position: str = "custom"
    rotate: Optional[Union[HFloat, RotateSettings]] = None
    resize: Optional[Union[Literal["cover", "fill", "fit", "contain"], str]] = None
    crop: Optional[CropSettings] = None
    correction: Optional[CorrectionSettings] = None
