from typing import Optional, Literal, Union
from pydantic import Field
from .base import J2VElement, HInt, HFloat, HBool
from .settings import RotateSettings, CropSettings, CorrectionSettings

class AudiogramElement(J2VElement):
    type: Literal["audiogram"] = "audiogram"
    color: str = Field("#ffffff", description="Waveform color")
    
    # Hybrid settings
    amplitude: HFloat = Field(5.0, description="Waveform amplitude")
    opacity: HFloat = 0.5
    width: HInt = Field(-1, description="Waveform width")
    height: HInt = Field(-1, description="Waveform height")
    x: HInt = Field(0, description="X coordinate")
    y: HInt = Field(0, description="Y coordinate")
    
    position: str = "custom"
    rotate: Optional[Union[HFloat, RotateSettings]] = None
    resize: Optional[Union[Literal["cover", "fill", "fit", "contain"], str]] = None
    crop: Optional[CropSettings] = None
    correction: Optional[CorrectionSettings] = None
