from datetime import datetime

from pydantic import BaseModel, Field, ValidationError, field_validator


class DatetimeToTimestampRequest(BaseModel):
    """Wejście scenariusza datetime → timestamp."""

    datetime_iso: str = Field(..., description="Datetime w formacie ISO 8601")

    @field_validator("datetime_iso")
    @classmethod
    def validate_datetime_iso(cls, value: str) -> str:
        try:
            # Walidacja formatu ISO 8601; dopuszczamy zarówno z, jak i bez strefy
            datetime.fromisoformat(value)
        except ValueError as exc:  # noqa: B904
            raise ValidationError(
                [f"Invalid ISO 8601 datetime string: {value}"], cls  # type: ignore[arg-type]
            ) from exc
        return value


class DatetimeToTimestampResult(BaseModel):
    """Wyjście scenariusza datetime → timestamp."""

    timestamp: float = Field(..., description="Unix timestamp w sekundach (float)")

