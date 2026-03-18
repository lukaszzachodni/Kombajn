from typing import Any, Dict, Optional, Union, Literal
from pydantic import Field
from .base import J2VElement
from .settings import RotateSettings, CropSettings, CorrectionSettings

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
