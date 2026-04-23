from pydantic import BaseModel, Field

class CropSettings(BaseModel):
    model_config = {"populate_by_name": True}
    width: int = Field(..., description="Crop width")
    height: int = Field(..., description="Crop height")
    x: int = Field(0, description="Crop X start point")
    y: int = Field(0, description="Crop Y start point")
