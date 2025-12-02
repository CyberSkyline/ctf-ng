"""
Base validation framework - reusable across domains.
"""

from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from functools import wraps
from typing import Any

from CTFd.models import get_class_by_tablename, Users

from . import utc_now
from ..exceptions import ValidationError

def validation_field(func: Callable) -> Callable:
    """
    Decorator to handle common validation patterns:
    - Extract and format friendly_name
    - Handle required field validation
    - Early return for None values on non-required fields
    """

    @wraps(func)
    def wrapper(
        self,
        data: dict[str, Any],
        field: str,
        *args,
        required: bool = False,
        friendly_name: str | None = None,
        **kwargs,
    ):
        # Extract friendly name
        name = friendly_name or field.replace("_", " ").title()
        value = data.get(field)

        # Handle required field validation
        if required:
            if field not in data or data.get(field) in [None, ""]:
                self.errors[field] = ValidationErrorMessages.FIELD_REQUIRED.format(field=name)
                return None

        # Early return for None values on non-required fields
        if value is None and not required:
            if field in data:
                # if none is explicitly provided, pass it through
                self._add_parsed_data(field, None)
            return None

        # Call the original function with the processed parameters
        return func(self, data, field, *args, friendly_name=name, value=value, required=required, **kwargs)

    return wrapper


class ValidationErrorMessages:
    """Consistent error messages throughout the system."""

    FIELD_REQUIRED = "{field} is required"
    FIELD_EMPTY = "{field} cannot be empty"
    FIELD_MUST_BE_STRING = "{field} must be a string"
    FIELD_MUST_BE_NUMBER = "{field} must be a valid number"
    FIELD_MUST_BE_BOOLEAN = "{field} must be true or false"
    FIELD_MUST_BE_POSITIVE = "{field} must be a positive number"
    FIELD_MUST_BE_DATETIME = "{field} must be a valid datetime in ISO format (YYYY-MM-DDTHH:MM:SS)"
    FIELD_DATETIME_MUST_BE_UTC = "{field} must be specified in UTC (Z or +00:00)"
    FIELD_DATETIME_PAST = "{field} cannot be in the past"
    FIELD_DATETIME_ORDER = "Start time must be before end time"
    FIELD_OUT_OF_RANGE = "{field} must be between {min_val} and {max_val}"
    FIELD_TOO_LONG = "{field} cannot be longer than {max_length} characters"


class BaseValidator:
    """Consolidates all common validation patterns."""

    def __init__(self):
        self.errors: dict[str, str] = {}
        self.parsed_data: dict[str, Any] = {}

    def _add_parsed_data(self, field: str, value: Any) -> None:
        """Internal helper to add data only if validation for that field has passed."""
        if field not in self.errors:
            if self.parsed_data.get(field) is not None:
                existing = self.parsed_data[field]
                if not isinstance(existing, list):
                    self.parsed_data[field] = [existing, value]
                else:
                    self.parsed_data[field].append(value)
            else:
                self.parsed_data[field] = value

    @validation_field
    def validate_string(
        self,
        data: dict[str, Any],
        field: str,
        # min_length : int | None = 1, # TODO - implement min_length
        max_length: int | None = None,
        required: bool = False,
        friendly_name: str | None = None,
        value: Any = None,  # Injected by decorator
        printable_only: bool = False,
        trim_whitespace: bool = True,
    ) -> None:
        if not isinstance(value, str):
            self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_STRING.format(field=friendly_name)
            return

        stripped_value = value.strip() if trim_whitespace else value
        if len(stripped_value) == 0 and required:
            self.errors[field] = ValidationErrorMessages.FIELD_EMPTY.format(field=friendly_name)
            return

        if max_length and len(stripped_value) > max_length:
            self.errors[field] = ValidationErrorMessages.FIELD_TOO_LONG.format(
                field=friendly_name, max_length=max_length
            )
            return

        if printable_only and (stripped_value.isprintable() is False or stripped_value.isascii() is False):
            self.errors[field] = f"{friendly_name} contains non-printable characters"
            return

        self._add_parsed_data(field, stripped_value)

    @validation_field
    def validate_string_list(
        self,
        data: dict[str, Any],
        field: str,
        max_length: int | None = None,
        required: bool = False,
        friendly_name: str | None = None,
        value: Any = None,  # Injected by decorator
        printable_only: bool = False,
        trim_whitespace: bool = True,
    ) -> None:
        if not isinstance(value, list):
            self.errors[field] = f"{friendly_name} must be a list of strings"
            return

        validated_list = []
        for item in value:
            if not isinstance(item, str):
                self.errors[field] = f"All items in {friendly_name} must be strings"
                return

            stripped_item = item.strip() if trim_whitespace else item
            if len(stripped_item) == 0:
                self.errors[field] = f"Items in {friendly_name} cannot be empty strings"
                return

            if max_length and len(stripped_item) > max_length:
                self.errors[field] = ValidationErrorMessages.FIELD_TOO_LONG.format(
                    field=friendly_name, max_length=max_length
                )
                return
            if printable_only and (stripped_item.isprintable() is False or stripped_item.isascii() is False):
                    self.errors[field] = f"Items in {friendly_name} contain non-printable characters"
                    return

            validated_list.append(stripped_item)

        self._add_parsed_data(field, validated_list)

    @validation_field
    def validate_model_id(
        self,
        data: dict[str, Any],
        field: str,
        model_name: str,
        required: bool = False,
        friendly_name: str | None = None,
        value: Any = None,  # Injected by decorator - must be last
    ) -> None:
        if not isinstance(value, int) or value <= 0:
            self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_NUMBER.format(field=friendly_name)
            return

        # Map model names to table names
        model_table_mapping = {
            "Announcement": "ng_announcements",
            "Attempt": "ng_attempts",
            "Challenge": "ng_challenges",
            "ChallengeTag": "ng_challenge_tags",
            "ChallengeVariable": "ng_challenge_variables",
            "ContainerBlueprint": "ng_container_blueprints",
            "Demographic": "ng_demographics",
            "Event": "ng_events",
            "FileUpload": "ng_file_uploads",
            "Hint": "ng_challenge_hints",
            "HintRedemption": "ng_hint_redemptions",
            "ManualPointAward": "ng_manual_point_awards",
            "Notification": "ng_notifications",
            "Permission": "ng_permissions",
            "Question": "ng_challenge_questions",
            "Role": "ng_roles",
            "Score": "ng_scores",
            "ScoreEvent": "ng_score_events",
            "Team": "ng_teams",
            "TeamMember": "ng_team_members",
            "Ticket": "ng_tickets",
            "TicketTag": "ng_ticket_tags",
            "TicketAttachment": "ng_ticket_attachments",
            "User": "ng_users",
            "Users": "users",  # CTFd's main users table
        }

        # Get the table name for the model
        table_name = model_table_mapping.get(model_name)
        if not table_name:
            self.errors[field] = f"{friendly_name} references an unknown model: {model_name}"
            return

        # Get the SQLAlchemy model class
        model_class = get_class_by_tablename(table_name)
        if not model_class:
            self.errors[field] = f"{friendly_name} references an unknown model: {model_name}"
            return

        # Check if an object with the given ID exists
        try:
            obj = model_class.query.filter_by(id=value).first()
            if not obj:
                self.errors[field] = f"{friendly_name} with ID {value} does not exist"
                return

            self._add_parsed_data(field, value)

        except Exception as e:
            self.errors[field] = f"Error validating {friendly_name}: {str(e)}"
            return

    @validation_field
    def validate_positive_integer(
        self,
        data: dict[str, Any],
        field: str,
        required: bool = False,
        friendly_name: str | None = None,
        value: Any = None,  # Injected by decorator
    ) -> None:
        """
        Validate a positive (greater than zero) integer
        """
        return self.validate_integer(
            data,
            field,
            min_value=1,
            required=required,
            friendly_name=friendly_name
        )

    @validation_field
    def validate_admin_id(
        self,
        data: dict[str, Any],
        field: str = "admin_id",
        required: bool = False,  # Used in decorator
        friendly_name: str | None = None,
        value: Any = None,  # Injected by decorator
    ) -> None:
        """
        Validate that a user ID belongs to an admin user
        """
        try:
            user_id = int(value)
        except (ValueError, TypeError):
            self.errors[field] = f"{friendly_name} must be a valid number"
            return

        user = Users.query.get(user_id)

        if not user:
            self.errors[field] = f"{friendly_name} with ID {user_id} does not exist"
            return

        if user.type != "admin":
            self.errors[field] = "User must be an admin to perform this action"
            return

        self._add_parsed_data(field, user_id)

    @validation_field
    def validate_integer(
        self,
        data: dict[str, Any],
        field: str,
        min_value: int | None = None,
        max_value: int | None = None,
        allow_zero: bool = True,
        required: bool = False,  # Used in decorator
        friendly_name: str | None = None,
        value: Any = None,  # Injected by decorator
    ) -> None:
        """
        Validate an integer field with optional constraints.
        """
        try:
            int_value = int(value)  # type: ignore[arg-type]

            # Check zero constraint
            if not allow_zero and int_value == 0:
                self.errors[field] = f"{friendly_name} cannot be zero"
                return

            # Check min constraint
            if min_value is not None and int_value < min_value:
                self.errors[field] = f"{friendly_name} must be at least {min_value}"
                return

            # Check max constraint
            if max_value is not None and int_value > max_value:
                self.errors[field] = f"{friendly_name} must be at most {max_value}"
                return

            self._add_parsed_data(field, int_value)

        except (ValueError, TypeError):
            self.errors[field] = f"{friendly_name} must be a valid integer"

    @validation_field
    def validate_integer_range(
        self,
        data: dict[str, Any],
        field: str,
        min_val: int,
        max_val: int,
        required: bool = False,
        friendly_name: str | None = None,
        value: Any = None,  # Injected by decorator
    ) -> None:
        # First validate as positive integer
        self.validate_positive_integer(data, field, required=required, friendly_name=friendly_name)

        if field in self.errors:
            return

        # The value should now be in parsed_data if validation passed
        int_value = int(self.parsed_data.get(field))  # type: ignore[arg-type]
        if not (min_val <= int_value <= max_val):
            self.errors[field] = ValidationErrorMessages.FIELD_OUT_OF_RANGE.format(
                field=friendly_name, min_val=min_val, max_val=max_val
            )
            if field in self.parsed_data:
                del self.parsed_data[field]

    @validation_field
    def validate_boolean(
        self,
        data: dict[str, Any],
        field: str,
        required: bool = False,
        friendly_name: str | None = None,
        value: Any = None,  # Injected by decorator
    ) -> None:
        if not isinstance(value, bool):
            self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_BOOLEAN.format(field=friendly_name)
            return

        self._add_parsed_data(field, value)

    @validation_field
    def validate_enum(
        self,
        data: dict[str, Any],
        field: str,
        enum_class: type[Enum],
        required: bool = False,
        friendly_name: str | None = None,
        value: Any = None,  # Injected by decorator
    ) -> None:
        try:
            enum_value = enum_class(value)
        except ValueError:
            self.errors[field] = f"{friendly_name} must be one of: {', '.join(e.name for e in enum_class)}"
            return
        self._add_parsed_data(field, enum_value)

    @validation_field
    def validate_datetime(
        self,
        data: dict[str, Any],
        field: str,
        allow_past: bool = True,
        required: bool = False,
        friendly_name: str | None = None,
        value: Any = None,  # Injected by decorator
    ) -> datetime | None:
        if not isinstance(value, str):
            self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_DATETIME.format(field=friendly_name)
            return None

        try:
            dt_value = datetime.fromisoformat(value)

            # require that tzinfo is set and is UTC
            if dt_value.tzinfo is not UTC:
                self.errors[field] = ValidationErrorMessages.FIELD_DATETIME_MUST_BE_UTC.format(field=friendly_name)
                return None

            if not allow_past and dt_value < utc_now():
                self.errors[field] = ValidationErrorMessages.FIELD_DATETIME_PAST.format(field=friendly_name)
                return None

            # SQLAlchemy expects to work with naive datetime objects (tzinfo=None),
            # so tzinfo must be removed here before sending this value to the model.
            # Leaving tzinfo as UTC here instead of changing it to None will break things.
            dt_value = dt_value.replace(tzinfo=None)

            self._add_parsed_data(field, dt_value)
            return dt_value
        except (ValueError, TypeError):
            self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_DATETIME.format(field=friendly_name)
            return None

    def validate(self) -> dict[str, Any]:
        """
        Validate and return parsed data if successful, or raise ValidationError if not.

        Returns:
            dict[str, Any]: The parsed and validated data

        Raises:
            ValidationError: If there are any validation errors
        """

        if self.errors:
            raise ValidationError("Validation failed", errors=self.errors)
        return self.parsed_data

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
        start_time = self.validate_datetime(data, start_field, required=False)
        end_time = self.validate_datetime(data, end_field, required=False)

        has_start = start_field in data and data.get(start_field) is not None
        has_end = end_field in data and data.get(end_field) is not None

        if has_start ^ has_end:  # XOR
            self.errors["time_constraint"] = (
                f"Both {start_field} and {end_field} must be provided together, or neither."
            )
            return

        if start_time and end_time and start_time >= end_time:
            self.errors[end_field] = (
                f"{end_field.replace('_', ' ').title()} must be after {start_field.replace('_', ' ')}."
            )
            return

    @validation_field
    def validate_url(
        self,
        data: dict[str, Any],
        field: str,
        required: bool = False,
        friendly_name: str | None = None,
        value: Any = None,  # Injected by decorator
    ) -> None:
        """
        Validate a URL string.
        """
        from urllib.parse import urlparse

        if not isinstance(value, str):
            self.errors[field] = ValidationErrorMessages.FIELD_MUST_BE_STRING.format(field=friendly_name)
            return

        parsed = urlparse(value)
        if not all([parsed.scheme, parsed.netloc]):
            self.errors[field] = f"{friendly_name} must be a valid URL"
            return

        self._add_parsed_data(field, value)



