"""
Domain specific validation functions using the base framework.
/backend/ng/core/utils/domain_validators.py
"""

from typing import Any, Union
from .validation_framework import BaseValidator, ValidationError
from ... import config


def validate_team_creation(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate team creation with the consolidated validator."""
    validator = BaseValidator()

    validator.validate_string(
        data,
        "name",
        config.TEAM_NAME_MAX_LENGTH,
        required=True,
        friendly_name="Team name",
    )
    validator.validate_positive_integer(data, "event_id", required=True, friendly_name="Event ID")

    # Validate optional fields
    validator.validate_boolean(data, "ranked", friendly_name="Ranked status")

    return validator.is_valid()


def validate_team_update(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate team updates."""
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
    return validator.is_valid()


def validate_team_leave(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate team leave requests."""
    validator = BaseValidator()
    validator.validate_positive_integer(data, "event_id", required=True, friendly_name="Event ID")
    return validator.is_valid()


def validate_team_join_by_code(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate invite code joins."""
    validator = BaseValidator()
    validator.validate_string(
        data,
        "invite_code",
        config.INVITE_CODE_MAX_LENGTH,
        required=True,
        friendly_name="Invite code",
    )
    return validator.is_valid()


def validate_captain_assignment(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate captain assignments."""
    validator = BaseValidator()
    validator.validate_positive_integer(data, "user_id", required=True, friendly_name="User ID")
    return validator.is_valid()


def validate_event_creation(data: dict[str, Any]) -> tuple[bool, dict]:
    """
    Validate event creation data.
    On success, returns a dictionary of parsed and typed values.
    On failure, returns a dictionary of error messages.
    """
    validator = BaseValidator()
    parsed_data = {}

    if validator.validate_string(
        data,
        "name",
        config.EVENT_NAME_MAX_LENGTH,
        required=True,
        friendly_name="Event name",
    ):
        parsed_data["name"] = data.get("name")

    if validator.validate_string(
        data,
        "description",
        config.EVENT_DESCRIPTION_MAX_LENGTH,
        friendly_name="Event description",
    ):
        if data.get("description") is not None:
            parsed_data["description"] = data.get("description")

    max_team_size_val = validator.validate_integer_range(
        data,
        "max_team_size",
        1,
        config.MAX_TEAM_SIZE,
        required=True,
        friendly_name="Max team size",
    )
    if max_team_size_val is not None:
        parsed_data["max_team_size"] = max_team_size_val

    if validator.validate_boolean(data, "locked", friendly_name="Locked status"):
        if "locked" in data:
            parsed_data["locked"] = data.get("locked")

    start_time_obj = validator.validate_datetime(data, "start_time", allow_past=False, friendly_name="Start time")
    if start_time_obj:
        parsed_data["start_time"] = start_time_obj

    end_time_obj = validator.validate_datetime(data, "end_time", allow_past=False, friendly_name="End time")
    if end_time_obj:
        parsed_data["end_time"] = end_time_obj

    if ("start_time" in parsed_data) != ("end_time" in parsed_data):
        if "start_time" not in parsed_data:
            validator.errors["start_time"] = "Start time is required when end time is provided"
        if "end_time" not in parsed_data:
            validator.errors["end_time"] = "End time is required when start time is provided"

    if "start_time" in parsed_data and "end_time" in parsed_data:
        if parsed_data["start_time"] >= parsed_data["end_time"]:
            validator.errors["end_time"] = ValidationError.FIELD_DATETIME_ORDER

    is_valid, errors = validator.is_valid()
    if not is_valid:
        return False, errors

    return True, parsed_data


def validate_event_registration_creation(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate event registration creation."""
    validator = BaseValidator()

    validator.validate_boolean(data, "public", friendly_name="Public registration")
    validator.validate_boolean(data, "reg_open", friendly_name="Registration open status")

    # Validate optional datetime fields
    reg_start_date = validator.validate_datetime(
        data, "reg_start_date", allow_past=False, friendly_name="Registration start date"
    )
    reg_end_date = validator.validate_datetime(
        data, "reg_end_date", allow_past=False, friendly_name="Registration end date"
    )

    # Check that if one time is provided, both must be provided
    if (reg_start_date is None) != (reg_end_date is None):
        if reg_start_date is None:
            validator.errors["reg_start_date"] = "Registration start date is required when end date is provided"
        if reg_end_date is None:
            validator.errors["reg_end_date"] = "Registration end date is required when start date is provided"

    # Check that start date is before end date
    if reg_start_date and reg_end_date and reg_start_date >= reg_end_date:
        validator.errors["reg_end_date"] = ValidationError.FIELD_DATETIME_ORDER

    return validator.is_valid()


def validate_join_event(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate joining an event."""
    validator = BaseValidator()

    # Validate required fields
    validator.validate_positive_integer(data, "event_id", required=True, friendly_name="Event ID")
    validator.validate_string(
        data,
        "invite_code",
        config.INVITE_CODE_MAX_LENGTH,
        required=False,
        friendly_name="Invite code",
    )
    validator.validate_string(
        data,
        "team_name",
        config.TEAM_NAME_MAX_LENGTH,
        required=False,
        friendly_name="Team name",
    )
    if not data.get("event_id"):
        validator.errors["event_id"] = "Event ID is required"
        
    # Ensure at least one of invite_code or team_name is provided
    if not data.get("invite_code") and not data.get("team_name"):
        validator.errors["fields"] = "Either invite_code or team_name must be provided"

    # Ensure only one of invite_code or team_name is provided
    if data.get("invite_code") and data.get("team_name"):
        validator.errors["fields"] = "Only one of invite_code or team_name can be provided"

    return validator.is_valid()


def validate_event_update(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate event updates."""
    validator = BaseValidator()

    if not any(
        data.get(field) is not None
        for field in [
            "name",
            "description",
            "max_team_size",
            "start_time",
            "end_time",
            "locked",
        ]
    ):
        validator.errors["fields"] = (
            "At least one field (name, description, max_team_size, start_time, end_time, or locked) must be provided"
        )
        return validator.is_valid()

    if "name" in data:
        validator.validate_string(data, "name", config.EVENT_NAME_MAX_LENGTH, friendly_name="Event name")
    if "description" in data:
        validator.validate_string(
            data,
            "description",
            config.EVENT_DESCRIPTION_MAX_LENGTH,
            friendly_name="Event description",
        )

    if "max_team_size" in data and data["max_team_size"] is not None:
        validator.validate_integer_range(
            data,
            "max_team_size",
            1,
            config.MAX_TEAM_SIZE,
            required=True,
            friendly_name="Max team size",
        )

    # Validate optional datetime fields
    start_time = None
    end_time = None
    if "start_time" in data:
        start_time = validator.validate_datetime(data, "start_time", allow_past=False, friendly_name="Start time")
    if "end_time" in data:
        end_time = validator.validate_datetime(data, "end_time", allow_past=False, friendly_name="End time")

    # Validate boolean field
    if "locked" in data:
        validator.validate_boolean(data, "locked", friendly_name="Locked status")

    # Check that if one time is provided, both must be provided (in updates)
    if ("start_time" in data) != ("end_time" in data):
        if "start_time" in data and "end_time" not in data:
            validator.errors["end_time"] = "End time must be provided when updating start time"
        if "end_time" in data and "start_time" not in data:
            validator.errors["start_time"] = "Start time must be provided when updating end time"

    # Check that start time is before end time
    if start_time and end_time and start_time >= end_time:
        validator.errors["end_time"] = ValidationError.FIELD_DATETIME_ORDER

    return validator.is_valid()


def validate_admin_reset(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate admin reset operations."""
    validator = BaseValidator()
    validator.validate_confirmation(data, config.ADMIN_RESET_CONFIRMATION)
    return validator.is_valid()


def validate_admin_event_reset(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate admin event reset operations."""
    validator = BaseValidator()
    validator.validate_confirmation(data, config.ADMIN_EVENT_RESET_CONFIRMATION)
    return validator.is_valid()


def validate_event_id_param(event_id: Union[str, int]) -> tuple[bool, dict[str, str]]:
    """Validate event_id from query parameters."""
    validator = BaseValidator()

    data = {"event_id": event_id}
    validator.validate_positive_integer(data, "event_id", required=True, friendly_name="Event ID")

    return validator.is_valid()
