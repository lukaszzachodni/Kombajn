from datetime import datetime
from pydantic import BaseModel, Field, ValidationError, field_validator

class DatetimeToTimestampRequest(BaseModel):
    """Scenario input: datetime → timestamp."""
    datetime_iso: str = Field(..., description="Datetime in ISO 8601 format")

    @field_validator("datetime_iso")
    @classmethod
    def validate_datetime_iso(cls, value: str) -> str:
        try:
            datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValidationError(
                [f"Invalid ISO 8601 datetime string: {value}"], cls
            ) from exc
        return value

class DatetimeToTimestampResult(BaseModel):
    """Scenario output: datetime → timestamp."""
    timestamp: float = Field(..., description="Unix timestamp in seconds (float)")
