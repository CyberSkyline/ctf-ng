"""
Event Registration Domain Validation
"""

from typing import Any
from ..utils.validator import BaseValidator
from ..exceptions import ValidationError

def validate_event_registration_creation(data: dict[str, Any]) -> dict[str, Any]:
    """Validate event registration creation data."""
    validator = BaseValidator()

    validator.validate_positive_integer(data, "event_id", required=True)
    validator.validate_boolean(data, "reg_open", required=False)
    validator.validate_boolean(data, "public", required=False)

    validator.validate_time_window(
        data,
        start_field="reg_start_date",
        end_field="reg_end_date",
    )

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Event registration creation data is invalid.", errors=errors)

    return parsed_data


def validate_join_event(data: dict[str, Any]) -> dict[str, Any]:
    """Validate joining an event."""
    print(f"Debug: validate_join_event called with data: {data}")
    validator = BaseValidator()

    if "invite_code" in data:
        validator.validate_string(data, "invite_code", 32, required=False, friendly_name="Invite code")
    if "team_name" in data:
        validator.validate_string(data, "team_name", 128, required=False, friendly_name="Team name")

    has_invite = "invite_code" in data and data.get("invite_code")
    has_name = "team_name" in data and data.get("team_name")

    if not has_invite and not has_name:
        validator.errors["general"] = "Either invite_code or team_name must be provided"
    elif has_invite and has_name:
        validator.errors["general"] = "Only one of invite_code or team_name can be provided"

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Join event data is invalid.", errors=errors)
    return parsed_data
