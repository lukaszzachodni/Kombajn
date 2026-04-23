from typing import List, Dict
from pydantic import BaseModel
from .main_project_details import MainProjectDetails
from .page_prompt import PagePrompt
from .language_version import LanguageVersion

class ColoringBook(BaseModel):
    mainProjectDetails: MainProjectDetails
    pagePromptLibrary: List[PagePrompt]
    languageVersions: Dict[str, LanguageVersion]
