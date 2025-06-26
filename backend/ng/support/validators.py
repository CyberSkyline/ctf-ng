"""
/backend/ng/support/validators.py
TEMPORARY Validation functions for support ticket operations.
"""

from typing import Any, Tuple
from ..core.utils.validation_framework import BaseValidator


def validate_ticket_creation(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate ticket creation data."""
    validator = BaseValidator()
    
    validator.validate_string(
        data,
        "subject",
        128,
        required=True,
        friendly_name="Ticket subject"
    )
    
    # Optional fields
    validator.validate_positive_integer(data, "event_id", required=False, friendly_name="Event ID")
    validator.validate_positive_integer(data, "team_id", required=False, friendly_name="Team ID")
    validator.validate_positive_integer(data, "challenge_id", required=False, friendly_name="Challenge ID")
    
    # Validate tag IDs if provided
    if "tag_ids" in data and data["tag_ids"] is not None:
        if not isinstance(data["tag_ids"], list):
            validator.errors["tag_ids"] = "Tag IDs must be a list"
        else:
            for idx, tag_id in enumerate(data["tag_ids"]):
                try:
                    int(tag_id)
                    if int(tag_id) <= 0:
                        validator.errors[f"tag_ids[{idx}]"] = "Tag ID must be positive"
                except (ValueError, TypeError):
                    validator.errors[f"tag_ids[{idx}]"] = "Tag ID must be a number"
    
    return validator.is_valid()


def validate_ticket_message(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate ticket message data."""
    validator = BaseValidator()
    
    validator.validate_string(
        data,
        "text",
        4096,
        required=True,
        friendly_name="Message text"
    )
    
    return validator.is_valid()


def validate_ticket_update(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate ticket update data."""
    validator = BaseValidator()
    
    # All fields are optional for updates
    if "subject" in data:
        validator.validate_string(
            data,
            "subject",
            128,
            required=False,
            friendly_name="Ticket subject"
        )
    
    if "event_id" in data:
        validator.validate_positive_integer(data, "event_id", required=False, friendly_name="Event ID")
    
    if "team_id" in data:
        validator.validate_positive_integer(data, "team_id", required=False, friendly_name="Team ID")
    
    if "challenge_id" in data:
        validator.validate_positive_integer(data, "challenge_id", required=False, friendly_name="Challenge ID")
    
    return validator.is_valid()


def validate_ticket_assignment(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate ticket assignment data."""
    validator = BaseValidator()
    
    validator.validate_positive_integer(data, "user_id", required=True, friendly_name="User ID")
    
    return validator.is_valid()


def validate_tag_creation(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate tag creation data."""
    validator = BaseValidator()
    
    validator.validate_string(
        data,
        "name",
        50,
        required=True,
        friendly_name="Tag name"
    )
    
    # Optional fields
    if "color" in data and data["color"] is not None:
        color = data["color"]
        if not isinstance(color, str) or not (len(color) == 7 and color.startswith("#")):
            validator.errors["color"] = "Color must be a valid hex code (e.g., #FF0000)"
    
    if "description" in data:
        validator.validate_string(
            data,
            "description",
            200,
            required=False,
            friendly_name="Tag description"
        )
    
    return validator.is_valid()


def validate_tag_update(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate tag update data."""
    validator = BaseValidator()
    
    # All fields are optional for updates
    if "name" in data:
        validator.validate_string(
            data,
            "name",
            50,
            required=False,
            friendly_name="Tag name"
        )
    
    if "color" in data and data["color"] is not None:
        color = data["color"]
        if not isinstance(color, str) or not (len(color) == 7 and color.startswith("#")):
            validator.errors["color"] = "Color must be a valid hex code (e.g., #FF0000)"
    
    if "description" in data:
        validator.validate_string(
            data,
            "description",
            200,
            required=False,
            friendly_name="Tag description"
        )
    
    return validator.is_valid()


def validate_ticket_filters(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate ticket list filter parameters."""
    validator = BaseValidator()
    
    # Optional filter parameters
    if "status" in data and data["status"] is not None:
        if data["status"] not in ["open", "closed", "muted", "all"]:
            validator.errors["status"] = "Status must be one of: open, closed, muted, all"
    
    if "assigned_to" in data:
        validator.validate_positive_integer(data, "assigned_to", required=False, friendly_name="Assigned to")
    
    if "event_id" in data:
        validator.validate_positive_integer(data, "event_id", required=False, friendly_name="Event ID")
    
    if "team_id" in data:
        validator.validate_positive_integer(data, "team_id", required=False, friendly_name="Team ID")
    
    return validator.is_valid()
