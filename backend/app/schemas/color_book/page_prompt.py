from pydantic import BaseModel

class PagePrompt(BaseModel):
    promptId: str
    sceneDescription: str
    graphicStyle: str
    emotionalTone: str
    complexityLevel: int
