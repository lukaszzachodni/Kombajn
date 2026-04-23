from typing import Any, Union, Annotated
from pydantic import AfterValidator

def validate_template(v: Any) -> Any:
    """
    Validator that allows strings containing {{...}} as valid values for any type.
    """
    if isinstance(v, str):
        if "{{" in v and "}}" in v:
            return v
        raise ValueError(f"Value '{v}' must be a template (e.g., '{{{{var}}}}') or a valid numeric value.")
    return v

# Hybrid Types for Template Support
HInt = Annotated[Union[int, str], AfterValidator(validate_template)]
HFloat = Annotated[Union[float, str], AfterValidator(validate_template)]
HBool = Annotated[Union[bool, str], AfterValidator(validate_template)]
