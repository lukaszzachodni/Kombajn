from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from backend.app.schemas.common.types import HInt, HBool

class SubtitlesSettings(BaseModel):
    model_config = {"populate_by_name": True}
    style: str = "classic"
    font_family: str = Field("Arial", alias="font-family")
    font_size: Optional[HInt] = Field(None, alias="font-size")
    font_color: str = Field("#ffffff", alias="font-color")
    font_url: Optional[str] = Field(None, alias="font-url")
    font_weight: str = Field("400", alias="font-weight")
    all_caps: HBool = Field(False, alias="all-caps")
    max_words_per_line: HInt = Field(4, alias="max-words-per-line")
    box_color: str = Field("#000000", alias="box-color")
    word_color: str = Field("#FFFF00", alias="word-color")
    line_color: str = Field("#FFFFFF", alias="line-color")
    outline_color: str = Field("#000000", alias="outline-color")
    outline_width: HInt = Field(0, alias="outline-width")
    shadow_color: str = Field("#000000", alias="shadow-color")
    shadow_offset: HInt = Field(0, alias="shadow-offset")
    position: str = "bottom-center"
    x: HInt = 0
    y: HInt = 0
    keywords: Optional[List[str]] = None
    replace: Optional[Dict[str, str]] = None
