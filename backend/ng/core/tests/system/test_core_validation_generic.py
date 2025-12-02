"""
Tests for generic validation utility functions
"""

import pytest
from enum import Enum
from datetime import timedelta, UTC

from CTFd.models import Users

from ...exceptions import ValidationError
from ...utils import utc_now
from ...utils.validator import BaseValidator

class TestBaseValidator:
    """Test the base validator functionality."""

    def test_validate_string(self):
        """Test string validation."""
        validator = BaseValidator()

        validator.validate_string({"name": "Valid"}, "name", max_length=10, required=True)
        parsed_data = validator.validate()
        assert parsed_data["name"] == "Valid"

        validator = BaseValidator()
        validator.validate_string({"name": "Too long"}, "name", max_length=5, required=True)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "name" in exc_info.value.errors

    def test_validate_positive_integer(self):
        """Test positive integer validation."""
        validator = BaseValidator()

        validator.validate_positive_integer({"num": 5}, "num", required=True)
        parsed_data = validator.validate()
        assert parsed_data["num"] == 5

        validator = BaseValidator()
        validator.validate_positive_integer({"num": -1}, "num", required=True)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "num" in exc_info.value.errors


class TestDatetimeValidationEdgeCases:
    """Test datetime validation edge cases."""

    def test_datetime_validation_various_formats(self):
        """Test datetime validation with various ISO formats."""
        validator = BaseValidator()

        dt = validator.validate_datetime({"time": "2024-12-25T10:30:00Z"}, "time")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 12
        assert dt.day == 25

        dt = validator.validate_datetime({"time": "2024-12-25T10:30:00Z"}, "time")
        assert dt is not None

        dt = validator.validate_datetime({"time": "2024-12-25T10:30:00.123456Z"}, "time")
        assert dt is not None
        assert dt.microsecond == 123456


    def test_datetime_past_validation(self):
        """Test datetime past validation."""
        validator = BaseValidator()

        future_date = (utc_now() + timedelta(days=1)).isoformat()
        dt = validator.validate_datetime({"time": future_date}, "time", allow_past=False)
        assert dt is not None

        past_date = (utc_now() - timedelta(days=1)).isoformat()
        dt = validator.validate_datetime({"time": past_date}, "time", allow_past=False)
        assert dt is None
        assert "time" in validator.errors

    def test_datetime_timezone_formats(self):
        """Test datetime validation with both Z and +00:00 timezone formats."""
        validator = BaseValidator()

        # Test Z format
        dt_z = validator.validate_datetime({"time": "2024-12-25T10:30:00Z"}, "time")
        assert dt_z is not None
        assert dt_z.year == 2024
        assert dt_z.month == 12
        assert dt_z.day == 25
        assert dt_z.hour == 10
        assert dt_z.minute == 30

        # Clear validator for next test
        validator = BaseValidator()

        # Test +00:00 format
        dt_plus = validator.validate_datetime({"time": "2024-12-25T10:30:00+00:00"}, "time")
        assert dt_plus is not None
        assert dt_plus.year == 2024
        assert dt_plus.month == 12
        assert dt_plus.day == 25
        assert dt_plus.hour == 10
        assert dt_plus.minute == 30

        # Both should result in the same datetime value
        assert dt_z == dt_plus

        # Clear validator for next test
        validator = BaseValidator()

        # Test microseconds with Z format
        dt_micro_z = validator.validate_datetime({"time": "2024-12-25T10:30:00.555777Z"}, "time")
        assert dt_micro_z is not None
        assert dt_micro_z.microsecond == 555777

        # Clear validator for next test
        validator = BaseValidator()

        # Test microseconds with +00:00 format
        dt_micro_plus = validator.validate_datetime({"time": "2024-12-25T10:30:00.555777+00:00"}, "time")
        assert dt_micro_plus is not None
        assert dt_micro_plus.microsecond == 555777

        # Both microsecond formats should result in the same datetime value
        assert dt_micro_z == dt_micro_plus


class TestPositiveIntegerEdgeCases:
    """Test positive integer validation edge cases."""

    def test_positive_integer_edge_values(self):
        """Test edge values for positive integer validation."""
        validator = BaseValidator()

        validator.validate_positive_integer({"num": 0}, "num")
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "num" in exc_info.value.errors
        assert "at least 1" in exc_info.value.errors["num"].lower()

        validator = BaseValidator()
        validator.validate_positive_integer({"num": -1}, "num")
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "num" in exc_info.value.errors

        validator = BaseValidator()
        validator.validate_positive_integer({"num": 5.0}, "num")
        parsed_data = validator.validate()
        assert parsed_data["num"] == 5



class TestStringValidationUnicode:
    """Test string validation with Unicode and edge cases."""

    def test_string_length_validation_unicode(self):
        """Test string validation with Unicode characters."""
        validator = BaseValidator()

        unicode_text = "café"
        validator.validate_string({"text": unicode_text}, "text", max_length=5, required=True)
        parsed_data = validator.validate()
        assert parsed_data["text"] == unicode_text

        validator = BaseValidator()
        long_unicode = "café" * 10
        validator.validate_string({"text": long_unicode}, "text", max_length=5, required=True)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "text" in exc_info.value.errors

    def test_string_whitespace_handling(self):
        """Test string validation with whitespace handling."""
        validator = BaseValidator()

        validator.validate_string({"text": "  valid content  "}, "text", required=True)
        parsed_data = validator.validate()
        assert parsed_data["text"] == "valid content"

        validator = BaseValidator()
        validator.validate_string({"text": "   "}, "text", required=True)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "text" in exc_info.value.errors

    def test_string_non_string_inputs(self):
        """
        Test string validation rejects non-string inputs
        """
        non_string_values = [123, [], {}, True, 3.14]

        for non_string_value in non_string_values:
            validator = BaseValidator()
            validator.validate_string({"field": non_string_value}, "field", required=True)
            with pytest.raises(ValidationError) as exc_info:
                validator.validate()
            assert "field" in exc_info.value.errors
            assert "must be a string" in exc_info.value.errors["field"]

        validator = BaseValidator()
        validator.validate_string({"field": None}, "field", required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "field" in exc_info.value.errors
        assert "is required" in exc_info.value.errors["field"]

    def test_string_rejects_non_printable(self):
        """
        Test string validation rejects non-printable characters
        """
        non_printable_strings = [
            "valid\x00string",  # Null byte
            "valid\x1Fstring",  # Unit separator
            "valid\x7Fstring",  # Delete character
        ]

        for test_string in non_printable_strings:
            validator = BaseValidator()
            validator.validate_string({"field": test_string}, "field", required=True, printable_only=True)
            with pytest.raises(ValidationError) as exc_info:
                validator.validate()
            assert "field" in exc_info.value.errors
            assert "contains non-printable characters" in exc_info.value.errors["field"]


class TestBooleanValidation:
    """Test boolean validation edge cases."""

    def test_boolean_validation_string_inputs(self):
        """Test boolean validation rejects string inputs."""
        validator = BaseValidator()

        string_values = ["true", "false", "True", "False", "yes", "no", "1", "0"]

        for string_value in string_values:
            validator = BaseValidator()
            validator.validate_boolean({"flag": string_value}, "flag")
            with pytest.raises(ValidationError) as exc_info:
                validator.validate()
            assert "flag" in exc_info.value.errors

    def test_boolean_validation_proper_types(self):
        """Test boolean validation with proper boolean types."""
        validator = BaseValidator()

        validator.validate_boolean({"flag": True}, "flag")
        parsed_data = validator.validate()
        assert parsed_data["flag"] is True

        validator = BaseValidator()
        validator.validate_boolean({"flag": False}, "flag")
        parsed_data = validator.validate()
        assert parsed_data["flag"] is False


class TestIntegerRangeValidation:
    """Test integer range validation."""

    def test_integer_range_boundaries(self):
        """Test integer validation at range boundaries."""
        validator = BaseValidator()

        validator.validate_integer_range({"size": 1}, "size", 1, 10)
        parsed_data = validator.validate()
        assert parsed_data["size"] == 1

        validator = BaseValidator()
        validator.validate_integer_range({"size": 10}, "size", 1, 10)
        parsed_data = validator.validate()
        assert parsed_data["size"] == 10

        validator = BaseValidator()
        validator.validate_integer_range({"size": 0}, "size", 1, 10)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "size" in exc_info.value.errors

        validator = BaseValidator()
        validator.validate_integer_range({"size": 11}, "size", 1, 10)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "size" in exc_info.value.errors

    def test_integer_range_error_message_format(self):
        """
        Test integer range validation error message format and cleanup behavior
        """
        validator = BaseValidator()
        validator.validate_integer_range({"size": 0}, "size", 1, 10)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "size" in exc_info.value.errors
        assert "must be at least 1" in exc_info.value.errors["size"]

        validator = BaseValidator()
        validator.validate_integer_range({"size": 15}, "size", 1, 10)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "size" in exc_info.value.errors
        assert "must be between 1 and 10" in exc_info.value.errors["size"]

        assert "size" not in validator.parsed_data


class TestAdminIdValidation:
    """
    Test admin ID validation
    """
    def test_validate_admin_id_success(self, db_session, admin):
        """
        Test validating a valid admin ID
        """
        validator = BaseValidator()
        validator.validate_admin_id({"admin_id": admin.id}, "admin_id", required=True)

        parsed_data = validator.validate()
        assert parsed_data["admin_id"] == admin.id

    def test_validate_admin_id_regular_user_fails(self, db_session, user):
        """
        Test that regular users are rejected for admin validation
        """
        validator = BaseValidator()
        validator.validate_admin_id({"admin_id": user.id}, "admin_id", required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "admin_id" in exc_info.value.errors
        assert "must be an admin" in exc_info.value.errors["admin_id"]

    def test_validate_admin_id_nonexistent_user(self, db_session):
        """
        Test validation with nonexistent user ID
        """
        validator = BaseValidator()
        validator.validate_admin_id({"admin_id": 999999}, "admin_id", required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "admin_id" in exc_info.value.errors
        assert "does not exist" in exc_info.value.errors["admin_id"]

    def test_validate_admin_id_invalid_types(self, db_session):
        """
        Test admin ID validation with invalid data types
        """
        invalid_values = [
            "not_a_number",
            "123abc",
            [],
            {},
            3.14
        ]

        for invalid_value in invalid_values:
            validator = BaseValidator()
            validator.validate_admin_id({"admin_id": invalid_value}, "admin_id", required=True)

            with pytest.raises(ValidationError) as exc_info:
                validator.validate()
            assert "admin_id" in exc_info.value.errors

        validator = BaseValidator()
        validator.validate_admin_id({"admin_id": None}, "admin_id", required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "admin_id" in exc_info.value.errors
        assert "is required" in exc_info.value.errors["admin_id"]

        validator = BaseValidator()
        validator.validate_admin_id({}, "admin_id", required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "admin_id" in exc_info.value.errors
        assert "is required" in exc_info.value.errors["admin_id"]

    def test_validate_admin_id_database(self, db_session, admin):
        """
        Test that admin validation queries the database correctly
        """
        db_admin = Users.query.get(admin.id)
        assert db_admin is not None
        assert db_admin.type == "admin"

        validator = BaseValidator()
        validator.validate_admin_id({"admin_id": admin.id}, "admin_id", required=True)

        parsed_data = validator.validate()
        assert parsed_data["admin_id"] == admin.id

        db_admin.type = "user"
        db_session.commit()

        validator = BaseValidator()
        validator.validate_admin_id({"admin_id": admin.id}, "admin_id", required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "admin_id" in exc_info.value.errors
        assert "must be an admin" in exc_info.value.errors["admin_id"]


class TestIntegerValidation:
    """
    Test integer validation with edge cases
    """
    def test_validate_integer_basic(self):
        """
        Test basic integer validation
        """
        validator = BaseValidator()
        validator.validate_integer({"num": 42}, "num", required=True)
        parsed_data = validator.validate()
        assert parsed_data["num"] == 42

    def test_validate_integer_with_constraints(self):
        """
        Test integer validation with min/max constraints
        """
        validator = BaseValidator()
        validator.validate_integer({"num": 5}, "num", min_value=1, max_value=10, required=True)
        parsed_data = validator.validate()
        assert parsed_data["num"] == 5

        validator = BaseValidator()
        validator.validate_integer({"num": 1}, "num", min_value=1, max_value=10, required=True)
        parsed_data = validator.validate()
        assert parsed_data["num"] == 1

        validator = BaseValidator()
        validator.validate_integer({"num": 10}, "num", min_value=1, max_value=10, required=True)
        parsed_data = validator.validate()
        assert parsed_data["num"] == 10

        validator = BaseValidator()
        validator.validate_integer({"num": 0}, "num", min_value=1, max_value=10, required=True)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "num" in exc_info.value.errors
        assert "must be at least 1" in exc_info.value.errors["num"]

        validator = BaseValidator()
        validator.validate_integer({"num": 11}, "num", min_value=1, max_value=10, required=True)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "num" in exc_info.value.errors
        assert "must be at most 10" in exc_info.value.errors["num"]

    def test_validate_integer_zero_handling(self):
        """
        Test integer validation zero constraint
        """
        validator = BaseValidator()
        validator.validate_integer({"num": 0}, "num", allow_zero=True, required=True)

        parsed_data = validator.validate()
        assert parsed_data["num"] == 0

        validator = BaseValidator()
        validator.validate_integer({"num": 0}, "num", allow_zero=False, required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "num" in exc_info.value.errors
        assert "cannot be zero" in exc_info.value.errors["num"]

    def test_validate_integer_type_coercion(self):
        """
        Test integer validation with type coercion
        """
        validator = BaseValidator()
        validator.validate_integer({"num": "42"}, "num", required=True)

        parsed_data = validator.validate()
        assert parsed_data["num"] == 42

        validator = BaseValidator()
        validator.validate_integer({"num": 42.0}, "num", required=True)

        parsed_data = validator.validate()
        assert parsed_data["num"] == 42

        validator = BaseValidator()
        validator.validate_integer({"num": 42.5}, "num", required=True)

        parsed_data = validator.validate()
        assert parsed_data["num"] == 42

        validator = BaseValidator()
        validator.validate_integer({"num": -42.9}, "num", required=True)

        parsed_data = validator.validate()
        assert parsed_data["num"] == -42

    def test_validate_integer_invalid_types(self):
        """
        Test integer validation with invalid types
        """
        invalid_values = [
            "not_a_number",
            [],
            {},
        ]

        for invalid_value in invalid_values:
            validator = BaseValidator()
            validator.validate_integer({"num": invalid_value}, "num", required=True)

            with pytest.raises(ValidationError) as exc_info:
                validator.validate()
            assert "num" in exc_info.value.errors
            assert "must be a valid integer" in exc_info.value.errors["num"]

        validator = BaseValidator()
        validator.validate_integer({"num": None}, "num", required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "num" in exc_info.value.errors
        assert "is required" in exc_info.value.errors["num"]

        validator = BaseValidator()
        validator.validate_integer({"num": "42.5"}, "num", required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "num" in exc_info.value.errors
        assert "must be a valid integer" in exc_info.value.errors["num"]

        validator = BaseValidator()
        validator.validate_integer({"num": True}, "num", required=True)

        parsed_data = validator.validate()
        assert parsed_data["num"] == 1

        validator = BaseValidator()
        validator.validate_integer({"num": False}, "num", required=True)

        parsed_data = validator.validate()
        assert parsed_data["num"] == 0


class TestEnumValidation:
    """
    Test enum validation with scenarios
    """
    def test_validate_enum_success(self):
        """
        Test enum validation with valid values
        """
        class TestEnum(Enum):
            OPTION_A = "a"
            OPTION_B = "b"
            OPTION_C = "c"

        validator = BaseValidator()
        validator.validate_enum({"choice": "a"}, "choice", TestEnum, required=True)

        parsed_data = validator.validate()
        assert parsed_data["choice"] == TestEnum.OPTION_A

        validator = BaseValidator()
        validator.validate_enum({"choice": "b"}, "choice", TestEnum, required=True)

        parsed_data = validator.validate()
        assert parsed_data["choice"] == TestEnum.OPTION_B

    def test_validate_enum_invalid_values(self):
        """
        Test enum validation with invalid values
        """
        class TestEnum(Enum):
            OPTION_A = "a"
            OPTION_B = "b"

        invalid_values = ["c", "invalid", 1, True, [], {}]

        for invalid_value in invalid_values:
            validator = BaseValidator()
            validator.validate_enum({"choice": invalid_value}, "choice", TestEnum, required=True)

            with pytest.raises(ValidationError) as exc_info:
                validator.validate()
            assert "choice" in exc_info.value.errors
            assert "must be one of" in exc_info.value.errors["choice"]
            assert "OPTION_A, OPTION_B" in exc_info.value.errors["choice"]

        validator = BaseValidator()
        validator.validate_enum({"choice": ""}, "choice", TestEnum, required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "choice" in exc_info.value.errors
        assert "is required" in exc_info.value.errors["choice"]

        validator = BaseValidator()
        validator.validate_enum({"choice": None}, "choice", TestEnum, required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "choice" in exc_info.value.errors
        assert "is required" in exc_info.value.errors["choice"]

    def test_validate_enum_integer_enum(self):
        """
        Test enum validation with integer-based enums
        """
        class StatusEnum(Enum):
            PENDING = 1
            APPROVED = 2
            REJECTED = 3

        validator = BaseValidator()
        validator.validate_enum({"status": 1}, "status", StatusEnum, required=True)

        parsed_data = validator.validate()
        assert parsed_data["status"] == StatusEnum.PENDING

        validator = BaseValidator()
        validator.validate_enum({"status": 4}, "status", StatusEnum, required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "status" in exc_info.value.errors


class TestDatetimeValidationMore:
    """
    More datetime validation tests beyond existing tests
    """
    def test_validate_datetime_utc_requirement(self):
        """
        Test that datetime validation requires UTC timezone
        """
        validator = BaseValidator()

        validator.validate_datetime({"dt": "2024-01-01T12:00:00+00:00"}, "dt", required=True)

        parsed_data = validator.validate()
        assert parsed_data["dt"] is not None

        validator = BaseValidator()
        validator.validate_datetime({"dt": "2024-01-01T12:00:00-05:00"}, "dt", required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "dt" in exc_info.value.errors
        assert "must be specified in UTC" in exc_info.value.errors["dt"]

        validator = BaseValidator()
        validator.validate_datetime({"dt": "2024-01-01T12:00:00"}, "dt", required=True)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "dt" in exc_info.value.errors


    def test_validate_datetime_invalid_formats(self):
        """
        Test datetime validation with more invalid formats"""

        invalid_datetimes = [
            "not-a-datetime",
            "2025-13-01T12:00:00Z",  # Invalid month
            "2025-08-32T12:00:00Z",  # Invalid day
            "2025-08-01T25:00:00Z",  # Invalid hour
            "2025-08-01T12:60:00Z",  # Invalid minute
            "2025-08-01T12:00:60Z",  # Invalid second
            "2025-08-01 12:00:00",   # Missing T separator and timezone
            "2025/08/01T12:00:00Z",  # Wrong date separator
            "",                      # Empty string
            123456789,               # Timestamp
            [],                      # List
            {},                      # Dict
        ]

        for invalid_dt in invalid_datetimes:
            validator = BaseValidator()
            validator.validate_datetime({"dt": invalid_dt}, "dt", required=True)

            with pytest.raises(ValidationError) as exc_info:
                validator.validate()
            assert "dt" in exc_info.value.errors

    def test_validate_datetime_timezone_conversion(self):
        """
        Test that UTC datetime gets properly converted for SQLAlchemy
        """
        validator = BaseValidator()
        validator.validate_datetime({"dt": "2024-01-01T12:00:00+00:00"}, "dt", required=True)
        parsed_data = validator.validate()

        assert parsed_data["dt"].tzinfo is None
        assert parsed_data["dt"].year == 2024
        assert parsed_data["dt"].month == 1
        assert parsed_data["dt"].day == 1
        assert parsed_data["dt"].hour == 12

    def test_validate_datetime_naive_datetime_fails(self):
        """
        Test that datetime validation fails for naive datetime strings (no timezone)
        """
        naive_datetimes = [
            "2025-08-01T12:00:00",      # No timezone info
            "2025-08-01T12:00:00.123",  # No timezone with microseconds
            "2025-08-01 12:00:00",      # Space separator, no timezone
        ]

        for naive_dt in naive_datetimes:
            validator = BaseValidator()
            validator.validate_datetime({"dt": naive_dt}, "dt", required=True)
            with pytest.raises(ValidationError) as exc_info:
                validator.validate()
            assert "dt" in exc_info.value.errors
            assert "must be specified in UTC" in exc_info.value.errors["dt"]


class TestTimeWindowValidation:
    """
    Test time window validation with scenarios
    """
    def test_validate_time_window_both_present(self):
        """
        Test time window validation when both start and end are present
        """
        start_time = (utc_now() + timedelta(hours=1)).replace(tzinfo=UTC).isoformat()
        end_time = (utc_now() + timedelta(hours=2)).replace(tzinfo=UTC).isoformat()

        validator = BaseValidator()
        validator.validate_time_window(
            {"start_time": start_time, "end_time": end_time},
            "start_time",
            "end_time"
        )
        parsed_data = validator.validate()
        assert "start_time" in parsed_data
        assert "end_time" in parsed_data

    def test_validate_time_window_both_missing(self):
        """
        Test time window validation when both start and end are missing
        """
        validator = BaseValidator()
        validator.validate_time_window({}, "start_time", "end_time")

        parsed_data = validator.validate()
        assert parsed_data == {}

    def test_validate_time_window_only_start(self):
        """
        Test time window validation fails when only start is present
        """
        start_time = (utc_now() + timedelta(hours=1)).replace(tzinfo=UTC).isoformat()

        validator = BaseValidator()
        validator.validate_time_window({"start_time": start_time}, "start_time", "end_time")

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "time_constraint" in exc_info.value.errors
        assert "must be provided together" in exc_info.value.errors["time_constraint"]

    def test_validate_time_window_only_end(self):
        """
        Test time window validation fails when only end is present
        """
        end_time = (utc_now() + timedelta(hours=2)).replace(tzinfo=UTC).isoformat()

        validator = BaseValidator()
        validator.validate_time_window({"end_time": end_time}, "start_time", "end_time")

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "time_constraint" in exc_info.value.errors
        assert "must be provided together" in exc_info.value.errors["time_constraint"]

    def test_validate_time_window_end_before_start(self):
        """
        Test time window validation fails when end is before start
        """
        start_time = (utc_now() + timedelta(hours=2)).replace(tzinfo=UTC).isoformat()
        end_time = (utc_now() + timedelta(hours=1)).replace(tzinfo=UTC).isoformat()

        validator = BaseValidator()
        validator.validate_time_window(
            {"start_time": start_time, "end_time": end_time},
            "start_time",
            "end_time"
        )
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "end_time" in exc_info.value.errors
        assert "must be after" in exc_info.value.errors["end_time"]

    def test_validate_time_window_equal_times(self):
        """
        Test time window validation fails when start equals end
        """
        same_time = (utc_now() + timedelta(hours=1)).replace(tzinfo=UTC).isoformat()

        validator = BaseValidator()
        validator.validate_time_window(
            {"start_time": same_time, "end_time": same_time},
            "start_time",
            "end_time"
        )
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "end_time" in exc_info.value.errors
        assert "must be after" in exc_info.value.errors["end_time"]
