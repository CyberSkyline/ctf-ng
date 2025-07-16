"""
Team Domain Validation
"""

from typing import Any

from ... import config
from ..utils.validator import BaseValidator


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

    return validator.validate()


def validate_team_leave(data: dict[str, Any]) -> dict[str, Any]:
    """Validate team leave request data. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_positive_integer(data, "event_id", required=True, friendly_name="Event ID")

    return validator.validate()


def validate_captain_assignment(data: dict[str, Any]) -> dict[str, Any]:
    """Validate captain assignment data. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_positive_integer(data, "user_id", required=True, friendly_name="User ID")

    return validator.validate()
