from pydantic import BaseModel

class CoverDetails(BaseModel):
    graphicStyle: str
    sceneDescription: str
