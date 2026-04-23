from typing import Any, Dict, Optional, Union, Literal
from pydantic import BaseModel, Field
from backend.app.schemas.common.types import HInt, HFloat, HBool
from .chroma_key_settings import ChromaKeySettings

class J2VElement(BaseModel):
    """Common properties for all JSON2Video elements with Template support."""
    model_config = {
        "protected_namespaces": (),
        "populate_by_name": True
    }
    
    type: str = Field(..., description="Element type")
    id: Optional[str] = Field(None, description="Unique element ID")
    comment: Optional[str] = Field(None, description="Internal notes (not rendered)")
    condition: Optional[Union[str, bool]] = Field(None, description="Expression to decide if element is rendered")
    variables: Optional[Dict[str, Any]] = Field(None, description="Local variables for this element")
    
    # Timing (Hybrid)
    start: HFloat = Field(0.0, description="Start time in seconds")
    duration: HFloat = Field(-2.0, description="Duration in seconds (-1: auto asset, -2: auto container)")
    extra_time: HFloat = Field(0.0, alias="extra-time", description="Additional time after completion")
    
    # Visuals (Hybrid)
    z_index: HInt = Field(0, alias="z-index", description="Stacking order (higher is on top)")
    fade_in: Optional[HFloat] = Field(None, alias="fade-in", description="Fade-in duration")
    fade_out: Optional[HFloat] = Field(None, alias="fade-out", description="Fade-out duration")
    mask: Optional[str] = Field(None, description="URL to mask file (PNG/Video)")
    chroma_key: Optional[ChromaKeySettings] = Field(None, alias="chroma-key")
    
    # Common Transformation (Hybrid)
    flip_horizontal: HBool = Field(False, alias="flip-horizontal", description="Flip horizontally")
    flip_vertical: HBool = Field(False, alias="flip-vertical", description="Flip vertically")
    zoom: HInt = Field(0, description="Zoom (-10 to 10)")
    pan: Optional[Union[Literal["left", "top", "right", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"], str]] = Field(None, description="Panning direction")
    pan_crop: HBool = Field(True, alias="pan-crop", description="Fill screen during panning")
    pan_distance: HFloat = Field(0.1, alias="pan-distance", description="Panning distance")

    cache: HBool = Field(True, description="Enable/disable caching for this element")
