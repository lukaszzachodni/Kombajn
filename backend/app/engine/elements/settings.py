from pydantic import BaseModel, Field

class ChromaKeySettings(BaseModel):
    model_config = {"populate_by_name": True}
    color: str = Field(..., description="Color to remove (e.g. #00b140 for green screen)")
    tolerance: int = Field(25, description="Chroma key sensitivity (1-100)")

class RotateSettings(BaseModel):
    model_config = {"populate_by_name": True}
    angle: float = Field(0.0, description="Rotation angle in degrees")
    speed: float = Field(0.0, description="Rotation speed for animation")

class CropSettings(BaseModel):
    model_config = {"populate_by_name": True}
    width: int = Field(..., description="Crop width")
    height: int = Field(..., description="Crop height")
    x: int = Field(0, description="Crop X start point")
    y: int = Field(0, description="Crop Y start point")

class CorrectionSettings(BaseModel):
    model_config = {"populate_by_name": True}
    brightness: float = Field(0.0, description="Brightness (-1.0 to 1.0)")
    contrast: float = Field(1.0, description="Contrast multiplier")
    gamma: float = Field(1.0, description="Gamma correction")
    saturation: float = Field(1.0, description="Saturation multiplier")
