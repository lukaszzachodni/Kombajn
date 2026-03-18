from typing import Optional, Literal, Union
from pydantic import Field
from .base import J2VElement
from .settings import RotateSettings, CropSettings, CorrectionSettings

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
