from pydantic import BaseModel, Field

class RotateSettings(BaseModel):
    model_config = {"populate_by_name": True}
    angle: float = Field(0.0, description="Rotation angle in degrees")
    speed: float = Field(0.0, description="Rotation speed for animation")
