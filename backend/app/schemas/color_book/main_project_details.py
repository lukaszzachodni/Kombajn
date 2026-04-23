from typing import List
from pydantic import BaseModel
from .author_name import AuthorName
from .cover_details import CoverDetails
from .page_idea import PageIdea

class MainProjectDetails(BaseModel):
    generationLanguage: str = "English"
    contentSafetyGuidelines: str = "Strictly adhere to content safety policies."
    title: str
    author: str
    suggestedUniversalAuthorName: AuthorName
    ageRange: str
    mainTheme: str
    creativeBrief: str
    artStyleGuidance: List[str]
    aspectRatio: str = "3:4"
    coloringPageGuidelines: str
    coverDetails: CoverDetails
    pageIdeas: List[PageIdea]
    numberOfPages: int = 40
