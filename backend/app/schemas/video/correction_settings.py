from pydantic import BaseModel, Field

class CorrectionSettings(BaseModel):
    model_config = {"populate_by_name": True}
    brightness: float = Field(0.0, description="Brightness (-1.0 to 1.0)")
    contrast: float = Field(1.0, description="Contrast multiplier")
    gamma: float = Field(1.0, description="Gamma correction")
    saturation: float = Field(1.0, description="Saturation multiplier")
