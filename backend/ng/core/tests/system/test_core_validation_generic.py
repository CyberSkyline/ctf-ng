"""
Tests for generic validation utility functions
"""

from datetime import timedelta

import pytest

from ...exceptions import ValidationError
from ...utils import utc_now
from ...validation import BaseValidator


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

    def test_datetime_validation_invalid_formats(self):
        """Test datetime validation with invalid formats."""
        validator = BaseValidator()
        invalid_formats = ["not a date", "2024-99-99", "invalid", "", "2024-12-25T10:30:00"]

        for invalid_format in invalid_formats:
            dt = validator.validate_datetime({"time": invalid_format}, "time")
            assert dt is None
            assert "time" in validator.errors
            validator.errors.clear()

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
        assert "positive" in exc_info.value.errors["num"].lower()

        validator = BaseValidator()
        validator.validate_positive_integer({"num": -1}, "num")
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "num" in exc_info.value.errors

        validator = BaseValidator()
        validator.validate_positive_integer({"num": 5.0}, "num")
        parsed_data = validator.validate()
        assert parsed_data["num"] == 5

    def test_positive_integer_invalid_types(self):
        """Test positive integer validation with invalid types."""
        validator = BaseValidator()

        invalid_values = [
            "not a number",
            "123abc",
            [1, 2, 3],
            {"nested": "dict"},
        ]

        for invalid_value in invalid_values:
            validator = BaseValidator()
            validator.validate_positive_integer({"num": invalid_value}, "num", required=True)
            with pytest.raises(ValidationError) as exc_info:
                validator.validate()
            assert "num" in exc_info.value.errors

        validator = BaseValidator()
        validator.validate_positive_integer({"num": None}, "num", required=True)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "num" in exc_info.value.errors

        validator = BaseValidator()
        validator.validate_positive_integer({"num": None}, "num", required=False)
        parsed_data = validator.validate()
        assert parsed_data == {}

        validator = BaseValidator()
        validator.validate_positive_integer({"num": 1}, "num")
        parsed_data = validator.validate()
        assert parsed_data["num"] == 1


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
