from datetime import datetime
from typing import List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, Field, ValidationError, field_validator


class DatetimeToTimestampRequest(BaseModel):
    """Scenario input: datetime → timestamp."""

    datetime_iso: str = Field(..., description="Datetime in ISO 8601 format")

    @field_validator("datetime_iso")
    @classmethod
    def validate_datetime_iso(cls, value: str) -> str:
        try:
            datetime.fromisoformat(value)
        except ValueError as exc:  # noqa: B904
            raise ValidationError(
                [f"Invalid ISO 8601 datetime string: {value}"], cls  # type: ignore[arg-type]
            ) from exc
        return value


class DatetimeToTimestampResult(BaseModel):
    """Scenario output: datetime → timestamp."""

    timestamp: float = Field(..., description="Unix timestamp in seconds (float)")


# --- VIDEO ORCHESTRATION SCHEMAS ---

class TextElement(BaseModel):
    """Text element on a scene."""
    type: Literal["text"] = "text"
    text: str
    font: str = "DejaVu-Sans"
    fontsize: int = 70
    color: str = "white"
    position: Union[str, Tuple[int, int], List[Union[str, int]]] = "center"
    start_time: float = 0.0
    end_time: Optional[float] = None
    duration: Optional[float] = None


class ColorBackground(BaseModel):
    """Solid color background."""
    type: Literal["color"] = "color"
    color: Union[str, Tuple[int, int, int]] = "black"
    duration: float


class ImageBackground(BaseModel):
    """Image background."""
    type: Literal["image"] = "image"
    path: str
    duration: float


class VideoBackground(BaseModel):
    """Video file background."""
    type: Literal["video"] = "video"
    path: str


# Polymorphic types
Background = Union[ColorBackground, ImageBackground, VideoBackground]
Element = Union[TextElement]


class Scene(BaseModel):
    """A single scene with background and overlaid elements."""
    background: Background
    elements: List[Element] = []
    duration: Optional[float] = None  # If None, use background duration


class VideoEditManifest(BaseModel):
    """Main video editing manifest definition."""
    project_id: str
    width: int = 1080
    height: int = 1920  # Default portrait format (Shorts)
    fps: int = 24
    scenes: List[Scene]
