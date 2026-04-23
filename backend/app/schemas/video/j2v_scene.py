from typing import List, Optional, Union, Dict, Any, Annotated
from pydantic import BaseModel, Field
from backend.app.schemas.common.types import HInt, HFloat, HBool

class J2VScene(BaseModel):
    model_config = {"populate_by_name": True}
    id: Optional[str] = Field(None, description="Scene identifier")
    comment: Optional[str] = None
    condition: Optional[Union[str, bool]] = None
    variables: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Scene-specific variables")
    iterate: Optional[str] = Field(None, description="Array to iterate over for dynamic scenes")
    background_color: str = Field("#000000", alias="background-color", description="Background color")
    duration: HFloat = Field(-1.0, description="Scene duration (-1 for auto)")
    cache: HBool = True
    elements: List[Any] = Field(default_factory=list, description="List of elements in the scene")
