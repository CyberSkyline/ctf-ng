"""
Event Domain Validation
"""

from typing import Any
from ..exceptions import ValidationError
from .framework import BaseValidator
from ... import config


def _validate_event_time_logic(validator: BaseValidator, data: dict[str, Any], is_update: bool = False):
    """Internal helper to validate the event's start and end times."""
    validator.validate_time_window(
        data,
        start_field="start_time",
        end_field="end_time",
        is_update=is_update,
        allow_past=False,
    )


def validate_event_creation(data: dict[str, Any]) -> dict[str, Any]:
    """Validate event creation input data."""
    validator = BaseValidator()

    validator.validate_string(
        data,
        "name",
        config.EVENT_NAME_MAX_LENGTH,
        required=True,
        friendly_name="Event name",
    )
    validator.validate_string(
        data,
        "description",
        config.EVENT_DESCRIPTION_MAX_LENGTH,
        required=False,
        friendly_name="Event description",
    )
    validator.validate_integer_range(
        data,
        "max_team_size",
        1,
        config.MAX_TEAM_SIZE,
        required=True,
        friendly_name="Max team size",
    )
    validator.validate_boolean(data, "locked", required=False, friendly_name="Locked status")

    _validate_event_time_logic(validator, data)

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Event creation data is invalid.", errors=errors)
    return parsed_data


def validate_event_update(data: dict[str, Any]) -> dict[str, Any]:
    """Validate event update input data."""
    validator = BaseValidator()

    if "name" in data:
        validator.validate_string(data, "name", config.EVENT_NAME_MAX_LENGTH, friendly_name="Event name")
    if "description" in data:
        validator.validate_string(
            data,
            "description",
            config.EVENT_DESCRIPTION_MAX_LENGTH,
            friendly_name="Event description",
        )
    if "max_team_size" in data:
        validator.validate_integer_range(
            data,
            "max_team_size",
            1,
            config.MAX_TEAM_SIZE,
            friendly_name="Max team size",
        )
    if "locked" in data:
        validator.validate_boolean(data, "locked", friendly_name="Locked status")

    _validate_event_time_logic(validator, data)

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Event update data is invalid.", errors=errors)
    return parsed_data


def validate_event_id_param(event_id: str | int) -> dict[str, Any]:
    """Validate event_id from query parameters."""
    validator = BaseValidator()
    data = {"event_id": event_id}
    validator.validate_positive_integer(data, "event_id", required=True, friendly_name="Event ID")

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Event ID parameter is invalid.", errors=errors)
    return parsed_data
