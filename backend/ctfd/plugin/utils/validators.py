# /plugin/utils/validators.py

from typing import Any, Optional, Union
from .. import config


class ValidationError:
    """Consistent error messages throughout the system."""

    FIELD_REQUIRED = "{field} is required"
    FIELD_EMPTY = "{field} cannot be empty"

    FIELD_MUST_BE_STRING = "{field} must be a string"
    FIELD_MUST_BE_NUMBER = "{field} must be a valid number"
    FIELD_MUST_BE_BOOLEAN = "{field} must be true or false"
    FIELD_MUST_BE_POSITIVE = "{field} must be a positive number"

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
    validator.validate_positive_integer(data, "world_id", required=True, friendly_name="World ID")

    # Validate optional fields
    validator.validate_integer_range(
        data,
        "limit",
        config.MIN_TEAM_SIZE,
        config.MAX_TEAM_SIZE,
        friendly_name="Team limit",
    )
    validator.validate_boolean(data, "ranked", friendly_name="Ranked status")

    return validator.is_valid()


def validate_team_update(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate team updates."""
    validator = BaseValidator()
    validator.validate_string(
        data,
        "name",
        config.TEAM_NAME_MAX_LENGTH,
        required=True,
        friendly_name="Team name",
    )
    return validator.is_valid()


def validate_team_join(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate team join requests."""
    validator = BaseValidator()
    validator.validate_positive_integer(data, "world_id", required=True, friendly_name="World ID")
    return validator.is_valid()


def validate_team_leave(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate team leave requests."""
    validator = BaseValidator()
    validator.validate_positive_integer(data, "world_id", required=True, friendly_name="World ID")
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


def validate_world_creation(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate world creation."""
    validator = BaseValidator()

    validator.validate_string(
        data,
        "name",
        config.WORLD_NAME_MAX_LENGTH,
        required=True,
        friendly_name="World name",
    )
    validator.validate_string(
        data,
        "description",
        config.WORLD_DESCRIPTION_MAX_LENGTH,
        friendly_name="World description",
    )
    validator.validate_integer_range(
        data,
        "default_team_size",
        config.MIN_TEAM_SIZE,
        config.MAX_TEAM_SIZE,
        friendly_name="Default team size",
    )

    return validator.is_valid()


def validate_world_update(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate world updates."""
    validator = BaseValidator()

    if not any(data.get(field) is not None for field in ["name", "description"]):
        validator.errors["fields"] = "At least one field (name or description) must be provided"
        return validator.is_valid()

    if "name" in data:
        validator.validate_string(data, "name", config.WORLD_NAME_MAX_LENGTH, friendly_name="World name")
    if "description" in data:
        validator.validate_string(
            data,
            "description",
            config.WORLD_DESCRIPTION_MAX_LENGTH,
            friendly_name="World description",
        )

    return validator.is_valid()


def validate_admin_reset(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate admin reset operations."""
    validator = BaseValidator()
    validator.validate_confirmation(data, config.ADMIN_RESET_CONFIRMATION)
    return validator.is_valid()


def validate_admin_world_reset(data: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate admin world reset operations."""
    validator = BaseValidator()
    validator.validate_confirmation(data, config.ADMIN_WORLD_RESET_CONFIRMATION)
    return validator.is_valid()


def validate_world_id_param(world_id: Union[str, int]) -> tuple[bool, dict[str, str]]:
    """Validate world_id from query parameters."""
    validator = BaseValidator()

    # Wrap the single param in a dict to reuse the main validation logic
    data = {"world_id": world_id}
    validator.validate_positive_integer(data, "world_id", required=True, friendly_name="World ID")

    return validator.is_valid()
