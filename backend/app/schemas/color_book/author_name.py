from pydantic import BaseModel

class AuthorName(BaseModel):
    firstName: str
    lastName: str
    fullDisplayName: str
