"""
Team Domain Validation
"""

from typing import Any
from ..exceptions import ValidationError
from ..utils.validator import BaseValidator
from ... import config


def validate_team_update(data: dict[str, Any]) -> dict[str, Any]:
    """Validate team update data. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_string(
        data,
        "name",
        config.TEAM_NAME_MAX_LENGTH,
        required=False,
        friendly_name="Team name",
    )
    validator.validate_boolean(data, "ranked", friendly_name="Ranked status")
    validator.validate_boolean(data, "locked", friendly_name="Locked status")

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Validation failed.", errors=errors)
    return parsed_data


def validate_team_leave(data: dict[str, Any]) -> dict[str, Any]:
    """Validate team leave request data. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_positive_integer(data, "event_id", required=True, friendly_name="Event ID")

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Validation failed.", errors=errors)
    return parsed_data


def validate_team_join_by_code(data: dict[str, Any]) -> dict[str, Any]:
    """Validate join by invite code data. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_string(
        data,
        "invite_code",
        config.INVITE_CODE_MAX_LENGTH,
        required=True,
        friendly_name="Invite code",
    )

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Join by invite code request is invalid.", errors=errors)
    return parsed_data


def validate_captain_assignment(data: dict[str, Any]) -> dict[str, Any]:
    """Validate captain assignment data. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_positive_integer(data, "user_id", required=True, friendly_name="User ID")

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Captain assignment data is invalid.", errors=errors)
    return parsed_data
