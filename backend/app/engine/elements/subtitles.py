from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, Field
from .base import J2VElement

class SubtitlesSettings(BaseModel):
    model_config = {"populate_by_name": True}
    style: str = "classic"
    font_family: str = Field("Arial", alias="font-family")
    font_size: Optional[int] = Field(None, alias="font-size")
    font_color: str = Field("#ffffff", alias="font-color")
    font_url: Optional[str] = Field(None, alias="font-url")
    font_weight: str = Field("400", alias="font-weight")
    all_caps: bool = Field(False, alias="all-caps")
    max_words_per_line: int = Field(4, alias="max-words-per-line")
    box_color: str = Field("#000000", alias="box-color")
    word_color: str = Field("#FFFF00", alias="word-color")
    line_color: str = Field("#FFFFFF", alias="line-color")
    outline_color: str = Field("#000000", alias="outline-color")
    outline_width: int = Field(0, alias="outline-width")
    shadow_color: str = Field("#000000", alias="shadow-color")
    shadow_offset: int = Field(0, alias="shadow-offset")
    position: str = "bottom-center"
    x: int = 0
    y: int = 0
    keywords: Optional[List[str]] = None
    replace: Optional[Dict[str, str]] = None

class SubtitlesElement(J2VElement):
    type: Literal["subtitles"] = "subtitles"
    captions: Optional[str] = Field(None, description="URL to SRT/VTT file or inline text")
    language: str = "auto"
    model: str = "default"
    settings: SubtitlesSettings = SubtitlesSettings()
