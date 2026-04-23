from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.common.types import HInt
from .j2v_scene import J2VScene

class J2VMovie(BaseModel):
    model_config = {"populate_by_name": True}
    width: HInt = Field(1920, description="Video width")
    height: HInt = Field(1080, description="Video height")
    fps: HInt = Field(24, description="Frames per second")
    resolution: Optional[str] = Field(None, description="Resolution alias (e.g. shorts)")
    quality: str = "high"
    draft: bool = False
    variables: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Global movie variables")
    scenes: List[J2VScene] = Field(default_factory=list, description="Movie scenes")
    elements: List[Any] = Field(default_factory=list, description="Global elements (overlaying all scenes)")
