from pydantic import BaseModel, Field

class ChromaKeySettings(BaseModel):
    model_config = {"populate_by_name": True}
    color: str = Field(..., description="Color to remove (e.g. #00b140 for green screen)")
    tolerance: int = Field(25, description="Chroma key sensitivity (1-100)")
