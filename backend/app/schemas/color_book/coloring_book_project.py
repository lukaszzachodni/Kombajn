from pydantic import BaseModel, Field
from .coloring_book import ColoringBook
from backend.app.schemas.common.ai_preferences import AIPreferences

class ColoringBookProject(BaseModel):
    ai_preferences: AIPreferences = Field(default_factory=AIPreferences)
    coloringBook: ColoringBook
