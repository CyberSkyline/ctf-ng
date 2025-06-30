"""
Admin Domain Validation
"""

from typing import Any
from ..exceptions import ValidationError
from .framework import BaseValidator
from ... import config


def validate_admin_reset(data: dict[str, Any]) -> dict[str, Any]:
    """Validate admin reset operations. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_confirmation(data, config.ADMIN_RESET_CONFIRMATION)

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Admin reset confirmation is invalid.", errors=errors)
    return parsed_data


def validate_admin_event_reset(data: dict[str, Any]) -> dict[str, Any]:
    """Validate admin event reset operations. Raises ValidationError on failure."""
    validator = BaseValidator()
    validator.validate_confirmation(data, config.ADMIN_EVENT_RESET_CONFIRMATION)

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Admin event reset confirmation is invalid.", errors=errors)
    return parsed_data
