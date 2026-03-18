from typing import Optional, Literal, Union
from pydantic import Field
from .base import J2VElement
from .settings import RotateSettings, CropSettings, CorrectionSettings

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
