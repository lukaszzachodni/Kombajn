from typing import List, Optional, Union, Dict, Any, Literal
from pydantic import BaseModel, Field, FieldValidationInfo, field_validator

class J2VElement(BaseModel):
    """Common properties for all JSON2Video elements."""
    type: str
    id: Optional[str] = None
    comment: Optional[str] = None
    condition: Optional[Union[str, bool]] = None
    variables: Optional[Dict[str, Any]] = None
    
    # Timing
    start: float = 0.0
    duration: float = -2.0  # -1: auto asset, -2: auto container
    extra_time: float = Field(0.0, alias="extra-time")
    
    # Visuals & Transitions
    z_index: int = Field(0, alias="z-index")
    fade_in: Optional[float] = Field(None, alias="fade-in")
    fade_out: Optional[float] = Field(None, alias="fade-out")
    cache: bool = True

    class Config:
        populate_by_name = True

class J2VScene(BaseModel):
    """Represents a segment of video content."""
    id: Optional[str] = None
    comment: Optional[str] = None
    condition: Optional[Union[str, bool]] = None
    variables: Optional[Dict[str, Any]] = None
    
    background_color: str = Field("#000000", alias="background-color")
    duration: float = -1.0  # -1: auto adjust to elements
    cache: bool = True
    elements: List[Dict[str, Any]] = []  # Polymorphic elements handled by factory

    class Config:
        populate_by_name = True

class J2VMovie(BaseModel):
    """Root object for a JSON2Video project."""
    width: int = 1920
    height: int = 1080
    fps: int = 24
    resolution: Optional[str] = None  # e.g., "full-hd", "shorts"
    quality: str = "high"
    draft: bool = False
    
    variables: Optional[Dict[str, Any]] = None
    scenes: List[J2VScene] = []
    elements: List[Dict[str, Any]] = []  # Global elements (watermarks, etc.)
    
    # Internal helpers for resolution mapping
    @field_validator("resolution")
    @classmethod
    def map_resolution(cls, v: Optional[str], info: FieldValidationInfo) -> Optional[str]:
        # Logic to update width/height based on string alias like "shorts" (1080x1920)
        # This will be expanded in the renderer
        return v
