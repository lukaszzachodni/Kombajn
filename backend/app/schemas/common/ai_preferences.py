from typing import Literal, Optional
from pydantic import BaseModel, Field

class AIPreferences(BaseModel):
    llm_provider: Literal["gemini", "local", "mock"] = Field("gemini", description="Provider for text and JSON generation")
    image_gen_provider: Literal["imagen", "local", "mock"] = Field("imagen", description="Provider for image generation")
    
    # Modele szczegółowe
    llm_model: Optional[str] = Field(None, description="Specific model name (e.g., gemini-1.5-flash)")
    image_gen_model: Optional[str] = Field(None, description="Specific model name (e.g., imagegeneration@006)")
