"""
/backend/ctfd/plugin/utils/validation_framework.py
Base validation framework - reusable across domains.
"""

from typing import Optional
from datetime import datetime


class ValidationError:
    """Consistent error messages throughout the system."""

    FIELD_REQUIRED = "{field} is required"
    FIELD_EMPTY = "{field} cannot be empty"

    FIELD_MUST_BE_STRING = "{field} must be a string"
    FIELD_MUST_BE_NUMBER = "{field} must be a valid number"
    FIELD_MUST_BE_BOOLEAN = "{field} must be true or false"
    FIELD_MUST_BE_POSITIVE = "{field} must be a positive number"
    FIELD_MUST_BE_DATETIME = "{field} must be a valid datetime in ISO format (YYYY-MM-DDTHH:MM:SS)"
    FIELD_DATETIME_PAST = "{field} cannot be in the past"
    FIELD_DATETIME_ORDER = "Start time must be before end time"

    FIELD_TOO_LONG = "{field} cannot exceed {max_length} characters"
    FIELD_OUT_OF_RANGE = "{field} must be between {min_val} and {max_val}"

    CONFIRMATION_INVALID = "You must send 'confirm': '{required_value}' to proceed with this operation"


class BaseValidator:
    """Consolidates all common validation patterns."""

    def __init__(self):
        self.errors = {}

    def require_field(self, data: dict, field: str, friendly_name: str = None) -> bool:
        """Check if a required field exists and has a value."""
        name = friendly_name or field.replace("_", " ").title()

        if field not in data or not data[field]:
            self.errors[field] = ValidationError.FIELD_REQUIRED.format(field=name)
            return False
        return True

    def validate_string(
        self,
        data: dict,
        field: str,
        max_length: int = None,
        required: bool = False,
        friendly_name: str = None,
    ) -> bool:
        """Validate string fields with consistent error messages."""
        name = friendly_name or field.replace("_", " ").title()
        value = data.get(field)

        if required and not self.require_field(data, field, name):
            return False

        if value is None:
            return True  # Optional field

        if not isinstance(value, str):
            self.errors[field] = ValidationError.FIELD_MUST_BE_STRING.format(field=name)
            return False

        if len(value.strip()) == 0 and required:
            self.errors[field] = ValidationError.FIELD_EMPTY.format(field=name)
            return False

        if max_length and len(value) > max_length:
            self.errors[field] = ValidationError.FIELD_TOO_LONG.format(field=name, max_length=max_length)
            return False

        return True

    def validate_positive_integer(
        self, data: dict, field: str, required: bool = False, friendly_name: str = None
    ) -> Optional[int]:
        """Validate positive integer fields consistently."""
        name = friendly_name or field.replace("_", " ").title()
        value = data.get(field)

        if required and not self.require_field(data, field, name):
            return None

        if value is None:
            return None  # Optional field

        try:
            int_value = int(value)
            if int_value <= 0:
                self.errors[field] = ValidationError.FIELD_MUST_BE_POSITIVE.format(field=name)
                return None
            return int_value
        except (ValueError, TypeError):
            self.errors[field] = ValidationError.FIELD_MUST_BE_NUMBER.format(field=name)
            return None

    def validate_integer_range(
        self,
        data: dict,
        field: str,
        min_val: int,
        max_val: int,
        required: bool = False,
        friendly_name: str = None,
    ) -> Optional[int]:
        """Validate integers within a specific range."""
        name = friendly_name or field.replace("_", " ").title()
        value = data.get(field)

        if not required and value is None:
            return None

        int_value = self.validate_positive_integer(data, field, required, name)
        if int_value is None:
            return None

        if not (min_val <= int_value <= max_val):
            self.errors[field] = ValidationError.FIELD_OUT_OF_RANGE.format(field=name, min_val=min_val, max_val=max_val)
            return None

        return int_value

    def validate_boolean(
        self, data: dict, field: str, required: bool = False, friendly_name: str = None
    ) -> Optional[bool]:
        """Validate boolean fields."""
        name = friendly_name or field.replace("_", " ").title()
        value = data.get(field)

        if not required and value is None:
            return None

        if not isinstance(value, bool):
            self.errors[field] = ValidationError.FIELD_MUST_BE_BOOLEAN.format(field=name)
            return None

        return value

    def validate_datetime(
        self,
        data: dict,
        field: str,
        required: bool = False,
        allow_past: bool = True,
        friendly_name: str = None,
    ) -> Optional[datetime]:
        """Validate datetime fields with ISO 8601 format."""
        name = friendly_name or field.replace("_", " ").title()
        value = data.get(field)

        if not required and value is None:
            return None

        if required and not self.require_field(data, field, name):
            return None

        if not isinstance(value, str):
            self.errors[field] = ValidationError.FIELD_MUST_BE_DATETIME.format(field=name)
            return None

        try:
            # Parse ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
            dt_value = datetime.fromisoformat(value.replace("Z", "+00:00"))

            if not allow_past and dt_value < datetime.now():
                self.errors[field] = ValidationError.FIELD_DATETIME_PAST.format(field=name)
                return None

            return dt_value

        except (ValueError, TypeError):
            self.errors[field] = ValidationError.FIELD_MUST_BE_DATETIME.format(field=name)
            return None

        return dt_value

    def validate_confirmation(self, data: dict, required_value: str) -> bool:
        """Validate destructive operation confirmations."""
        confirmation = data.get("confirm")

        if not confirmation:
            self.errors["confirmation"] = "Confirmation is required"
            return False

        if confirmation != required_value:
            self.errors["confirmation"] = ValidationError.CONFIRMATION_INVALID.format(required_value=required_value)
            return False

        return True

    def is_valid(self) -> tuple[bool, dict[str, str]]:
        """Return the validation results."""
        return len(self.errors) == 0, self.errors
