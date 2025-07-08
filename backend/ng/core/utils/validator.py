"""
Base validation framework - reusable across domains.
"""

from typing import Any
from datetime import datetime
from . import utc_now


class ValidationErrorMessages:
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
    FIELD_OUT_OF_RANGE = "{field} must be between {min_val} and {max_val}"
    FIELD_TOO_LONG = "{field} cannot be longer than {max_length} characters"
    CONFIRMATION_INVALID = "You must send 'confirm': '{required_value}' to proceed with this operation"


class BaseValidator:
    """Consolidates all common validation patterns."""

    def __init__(self):
        self.errors: dict[str, str] = {}
        self.parsed_data: dict[str, Any] = {}

    def _add_parsed_data(self, field: str, value: Any) -> None:
        """Internal helper to add data only if validation for that field has passed."""
        if field not in self.errors:
            self.parsed_data[field] = value

    def require_field(self, data: dict[str, Any], field: str, friendly_name: str | None = None) -> bool:
        name = friendly_name or field.replace("_", " ").title()
        if field not in data or data.get(field) in [None, ""]:
            self.errors[field] = ValidationErrorMessages.FIELD_REQUIRED.format(field=name)
            return False
        return True

    def validate_string(
        self,
        data: dict[str, Any],
        field: str,
        max_length: int | None = None,
        required: bool = False,
        friendly_name: str | None = None,
    ) -> None:
        name = friendly_name or field.replace("_", " ").title()
        value = data.get(field)

        if required and not self.require_field(data, field, name):
            return

        if value is None:
            return

        if not isinstance(value, str):
            self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_STRING.format(field=name)
            return

        stripped_value = value.strip()
        if len(stripped_value) == 0 and required:
            self.errors[field] = ValidationErrorMessages.FIELD_EMPTY.format(field=name)
            return

        if max_length and len(stripped_value) > max_length:
            self.errors[field] = ValidationErrorMessages.FIELD_TOO_LONG.format(field=name, max_length=max_length)
            return

        self._add_parsed_data(field, stripped_value)

    def validate_positive_integer(
        self,
        data: dict[str, Any],
        field: str,
        required: bool = False,
        friendly_name: str | None = None,
    ) -> None:
        name = friendly_name or field.replace("_", " ").title()
        value = data.get(field)

        if required and not self.require_field(data, field, name):
            return

        if value is None:
            return

        try:
            int_value = int(value)
            if int_value <= 0:
                self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_POSITIVE.format(field=name)
                return
            self._add_parsed_data(field, int_value)
        except (ValueError, TypeError):
            self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_NUMBER.format(field=name)

    def validate_integer_range(
        self,
        data: dict[str, Any],
        field: str,
        min_val: int,
        max_val: int,
        required: bool = False,
        friendly_name: str | None = None,
    ) -> None:
        name = friendly_name or field.replace("_", " ").title()

        self.validate_positive_integer(data, field, required, name)

        if field in self.errors:
            return

        value = data.get(field)
        if value is None and not required:
            return

        int_value = self.parsed_data.get(field)
        if not (min_val <= int_value <= max_val):
            self.errors[field] = ValidationErrorMessages.FIELD_OUT_OF_RANGE.format(
                field=name, min_val=min_val, max_val=max_val
            )
            if field in self.parsed_data:
                del self.parsed_data[field]

    def validate_boolean(
        self,
        data: dict[str, Any],
        field: str,
        required: bool = False,
        friendly_name: str | None = None,
    ) -> None:
        name = friendly_name or field.replace("_", " ").title()
        value = data.get(field)

        if required and not self.require_field(data, field, name):
            if value is not False:
                return

        if value is None:
            return

        if not isinstance(value, bool):
            self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_BOOLEAN.format(field=name)
            return

        self._add_parsed_data(field, value)

    def validate_datetime(
        self,
        data: dict[str, Any],
        field: str,
        required: bool = False,
        allow_past: bool = True,
        friendly_name: str | None = None,
    ) -> datetime | None:
        name = friendly_name or field.replace("_", " ").title()
        value = data.get(field)

        if not required and value is None:
            return None

        if required and not self.require_field(data, field, name):
            return None

        if not isinstance(value, str):
            self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_DATETIME.format(field=name)
            return None

        try:
            dt_value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if not allow_past and dt_value < utc_now():
                self.errors[field] = ValidationErrorMessages.FIELD_DATETIME_PAST.format(field=name)
                return None

            self._add_parsed_data(field, dt_value)
            return dt_value
        except (ValueError, TypeError):
            self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_DATETIME.format(field=name)
            return None

    def is_valid(self) -> tuple[bool, dict[str, str], dict[str, Any]]:
        """
        Return the validation results and the dictionary of parsed, valid data.
        """
        return len(self.errors) == 0, self.errors, self.parsed_data

    def validate_time_window(
        self,
        data: dict[str, Any],
        start_field: str,
        end_field: str,
    ):
        """
        Validates a start/end time window, ensuring both or neither are present
        and that start is before end.
        """
        start_time = self.validate_datetime(data, start_field, required=False, allow_past=False)
        end_time = self.validate_datetime(data, end_field, required=False, allow_past=False)

        has_start = start_field in data and data.get(start_field) is not None
        has_end = end_field in data and data.get(end_field) is not None

        if has_start ^ has_end:  # XOR
            self.errors["time_constraint"] = (f"Both {start_field} and {end_field} must be provided together, or neither.")
            return

        if start_time and end_time and start_time >= end_time:
            self.errors[end_field] = (f"{end_field.replace('_', ' ').title()} must be after {start_field.replace('_', ' ')}.")
            return
        
        
