from pydantic import BaseModel
from .uploader_data import UploaderData

class LanguageVersion(BaseModel):
    uploaderData: UploaderData
