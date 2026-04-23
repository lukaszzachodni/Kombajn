from pydantic import BaseModel

class PageIdea(BaseModel):
    pageNumber: int
    promptReferenceId: str
