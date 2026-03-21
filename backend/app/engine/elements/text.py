from typing import Any, Dict, Optional, Union, Literal
from pydantic import Field
from .base import J2VElement, HInt, HFloat, HBool
from .settings import RotateSettings

class TextElement(J2VElement):
    type: Literal["text"] = "text"
    text: str = Field(..., description="Text content")
    style: str = Field("001", description="Text animation style ID")
    settings: Dict[str, Any] = Field(default_factory=dict, description="CSS-like text settings")
    
    # Dimensions (Hybrid)
    width: HInt = Field(-1, description="Text box width")
    height: HInt = Field(-1, description="Text box height")
    x: HInt = Field(0, description="X coordinate")
    y: HInt = Field(0, description="Y coordinate")
    
    position: str = "custom"
    rotate: Optional[Union[HFloat, RotateSettings]] = None
