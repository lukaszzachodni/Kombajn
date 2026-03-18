from typing import Any, Dict, Optional, Union, Literal
from pydantic import BaseModel, Field
from .base import J2VElement
from .settings import RotateSettings

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
