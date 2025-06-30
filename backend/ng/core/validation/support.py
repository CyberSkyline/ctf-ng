"""
Support Domain Validation
"""

from typing import Any
from ..exceptions import ValidationError
from .framework import BaseValidator


def validate_ticket_creation(data: dict[str, Any]) -> dict[str, Any]:
    """Validate ticket creation data. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_string(data, "subject", 128, required=True, friendly_name="Ticket subject")
    validator.validate_positive_integer(data, "event_id", required=False, friendly_name="Event ID")
    validator.validate_positive_integer(data, "team_id", required=False, friendly_name="Team ID")
    validator.validate_positive_integer(data, "challenge_id", required=False, friendly_name="Challenge ID")

    if "tag_ids" in data and data["tag_ids"] is not None:
        if not isinstance(data["tag_ids"], list):
            validator.errors["tag_ids"] = "Tag IDs must be a list of numbers"
        else:
            for idx, tag_id in enumerate(data["tag_ids"]):
                if not isinstance(tag_id, int) or tag_id <= 0:
                    validator.errors[f"tag_ids.{idx}"] = "Each tag ID must be a positive integer"

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Ticket creation data is invalid.", errors=errors)
    return parsed_data


def validate_ticket_message(data: dict[str, Any]) -> dict[str, Any]:
    """Validate ticket message data. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_string(data, "text", 4096, required=True, friendly_name="Message text")

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Ticket message data is invalid.", errors=errors)
    return parsed_data


def validate_ticket_update(data: dict[str, Any]) -> dict[str, Any]:
    """Validate ticket update data. Raises ValidationError on failure."""
    validator = BaseValidator()
    if "subject" in data:
        validator.validate_string(data, "subject", 128, required=False, friendly_name="Ticket subject")
    if "event_id" in data:
        validator.validate_positive_integer(data, "event_id", required=False, friendly_name="Event ID")
    if "team_id" in data:
        validator.validate_positive_integer(data, "team_id", required=False, friendly_name="Team ID")
    if "challenge_id" in data:
        validator.validate_positive_integer(data, "challenge_id", required=False, friendly_name="Challenge ID")

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Ticket update data is invalid.", errors=errors)
    return parsed_data


def validate_ticket_assignment(data: dict[str, Any]) -> dict[str, Any]:
    """Validate ticket assignment data. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_positive_integer(data, "user_id", required=True, friendly_name="User ID")

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Ticket assignment data is invalid.", errors=errors)
    return parsed_data


def validate_tag_creation(data: dict[str, Any]) -> dict[str, Any]:
    """Validate tag creation data. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_string(data, "name", 50, required=True, friendly_name="Tag name")
    if "color" in data and data["color"] is not None:
        color = data["color"]
        if not isinstance(color, str) or not (len(color) == 7 and color.startswith("#")):
            validator.errors["color"] = "Color must be a valid hex code (e.g., #FF0000)"
    if "description" in data:
        validator.validate_string(data, "description", 200, required=False, friendly_name="Tag description")

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Tag creation data is invalid.", errors=errors)
    return parsed_data


def validate_tag_update(data: dict[str, Any]) -> dict[str, Any]:
    """Validate tag update data. Raises ValidationError on failure."""
    validator = BaseValidator()
    if "name" in data:
        validator.validate_string(data, "name", 50, required=False, friendly_name="Tag name")
    if "color" in data and data["color"] is not None:
        color = data["color"]
        if not isinstance(color, str) or not (len(color) == 7 and color.startswith("#")):
            validator.errors["color"] = "Color must be a valid hex code (e.g., #FF0000)"
    if "description" in data:
        validator.validate_string(data, "description", 200, required=False, friendly_name="Tag description")

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Tag update data is invalid.", errors=errors)
    return parsed_data


def validate_ticket_filters(data: dict[str, Any]) -> dict[str, Any]:
    """Validate ticket filter data. Raises ValidationError on failure."""
    validator = BaseValidator()
    if "status" in data and data["status"] is not None:
        if data["status"] not in ["open", "closed", "muted", "all"]:
            validator.errors["status"] = "Status must be one of: open, closed, muted, all"
    if "assigned_to" in data:
        validator.validate_positive_integer(data, "assigned_to", required=False, friendly_name="Assigned to")
    if "event_id" in data:
        validator.validate_positive_integer(data, "event_id", required=False, friendly_name="Event ID")
    if "team_id" in data:
        validator.validate_positive_integer(data, "team_id", required=False, friendly_name="Team ID")

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Ticket filter data is invalid.", errors=errors)
    return parsed_data
