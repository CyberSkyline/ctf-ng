"""
Tests for generic validation utility functions
"""

from datetime import timedelta
from ...validation import BaseValidator
from ...utils import utc_now


class ValidationError(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors or {}
        super().__init__(message)


class TestBaseValidator:
    """Test the base validator functionality."""

    def test_validate_string(self):
        """Test string validation."""
        validator = BaseValidator()

        validator.validate_string({"name": "Valid"}, "name", max_length=10, required=True)
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid is True
        assert parsed_data["name"] == "Valid"

        validator = BaseValidator()
        validator.validate_string({"name": "Too long"}, "name", max_length=5, required=True)
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid is False
        assert "name" in errors

    def test_validate_positive_integer(self):
        """Test positive integer validation."""
        validator = BaseValidator()

        validator.validate_positive_integer({"num": 5}, "num", required=True)
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid is True
        assert parsed_data["num"] == 5

        validator = BaseValidator()
        validator.validate_positive_integer({"num": -1}, "num", required=True)
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid is False
        assert "num" in errors


class TestDatetimeValidationEdgeCases:
    """Test datetime validation edge cases."""

    def test_datetime_validation_various_formats(self):
        """Test datetime validation with various ISO formats."""
        validator = BaseValidator()

        dt = validator.validate_datetime({"time": "2024-12-25T10:30:00"}, "time")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 12
        assert dt.day == 25

        dt = validator.validate_datetime({"time": "2024-12-25T10:30:00Z"}, "time")
        assert dt is not None

        dt = validator.validate_datetime({"time": "2024-12-25T10:30:00.123456"}, "time")
        assert dt is not None
        assert dt.microsecond == 123456

    def test_datetime_validation_invalid_formats(self):
        """Test datetime validation with invalid formats."""
        validator = BaseValidator()
        invalid_formats = ["not a date", "2024-99-99", "invalid", ""]

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


class TestPositiveIntegerEdgeCases:
    """Test positive integer validation edge cases."""

    def test_positive_integer_edge_values(self):
        """Test edge values for positive integer validation."""
        validator = BaseValidator()

        validator.validate_positive_integer({"num": 0}, "num")
        is_valid, errors, parsed_data = validator.is_valid()
        assert not is_valid
        assert "num" in errors
        assert "positive" in errors["num"].lower()

        validator = BaseValidator()
        validator.validate_positive_integer({"num": -1}, "num")
        is_valid, errors, parsed_data = validator.is_valid()
        assert not is_valid
        assert "num" in errors

        validator = BaseValidator()
        validator.validate_positive_integer({"num": 5.0}, "num")
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid
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
            is_valid, errors, parsed_data = validator.is_valid()
            assert not is_valid
            assert "num" in errors

        validator = BaseValidator()
        validator.validate_positive_integer({"num": None}, "num", required=True)
        is_valid, errors, parsed_data = validator.is_valid()
        assert not is_valid
        assert "num" in errors

        validator = BaseValidator()
        validator.validate_positive_integer({"num": None}, "num", required=False)
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid

        validator = BaseValidator()
        validator.validate_positive_integer({"num": 1}, "num")
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid
        assert parsed_data["num"] == 1


class TestStringValidationUnicode:
    """Test string validation with Unicode and edge cases."""

    def test_string_length_validation_unicode(self):
        """Test string validation with Unicode characters."""
        validator = BaseValidator()

        unicode_text = "café"
        validator.validate_string({"text": unicode_text}, "text", max_length=5, required=True)
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid
        assert parsed_data["text"] == unicode_text

        validator = BaseValidator()
        long_unicode = "café" * 10
        validator.validate_string({"text": long_unicode}, "text", max_length=5, required=True)
        is_valid, errors, parsed_data = validator.is_valid()
        assert not is_valid
        assert "text" in errors

    def test_string_whitespace_handling(self):
        """Test string validation with whitespace handling."""
        validator = BaseValidator()

        validator.validate_string({"text": "  valid content  "}, "text", required=True)
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid
        assert parsed_data["text"] == "valid content"

        validator = BaseValidator()
        validator.validate_string({"text": "   "}, "text", required=True)
        is_valid, errors, parsed_data = validator.is_valid()
        assert not is_valid
        assert "text" in errors


class TestBooleanValidation:
    """Test boolean validation edge cases."""

    def test_boolean_validation_string_inputs(self):
        """Test boolean validation rejects string inputs."""
        validator = BaseValidator()

        string_values = ["true", "false", "True", "False", "yes", "no", "1", "0"]

        for string_value in string_values:
            validator = BaseValidator()
            validator.validate_boolean({"flag": string_value}, "flag")
            is_valid, errors, parsed_data = validator.is_valid()
            assert not is_valid
            assert "flag" in errors

    def test_boolean_validation_proper_types(self):
        """Test boolean validation with proper boolean types."""
        validator = BaseValidator()

        validator.validate_boolean({"flag": True}, "flag")
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid
        assert parsed_data["flag"] is True

        validator = BaseValidator()
        validator.validate_boolean({"flag": False}, "flag")
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid
        assert parsed_data["flag"] is False


class TestConfirmationValidation:
    """Test confirmation validation."""

    def test_confirmation_validation_case_sensitivity(self):
        """Test that confirmation is case-sensitive."""
        validator = BaseValidator()

        required_value = "DELETE ALL DATA"

        validator.validate_confirmation({"confirm": "DELETE ALL DATA"}, required_value)
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid
        assert parsed_data["confirm"] == "DELETE ALL DATA"

        validator = BaseValidator()
        validator.validate_confirmation({"confirm": "delete all data"}, required_value)
        is_valid, errors, parsed_data = validator.is_valid()
        assert not is_valid
        assert "confirmation" in errors


class TestIntegerRangeValidation:
    """Test integer range validation."""

    def test_integer_range_boundaries(self):
        """Test integer validation at range boundaries."""
        validator = BaseValidator()

        validator.validate_integer_range({"size": 1}, "size", 1, 10)
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid
        assert parsed_data["size"] == 1

        validator = BaseValidator()
        validator.validate_integer_range({"size": 10}, "size", 1, 10)
        is_valid, errors, parsed_data = validator.is_valid()
        assert is_valid
        assert parsed_data["size"] == 10

        validator = BaseValidator()
        validator.validate_integer_range({"size": 0}, "size", 1, 10)
        is_valid, errors, parsed_data = validator.is_valid()
        assert not is_valid
        assert "size" in errors

        validator = BaseValidator()
        validator.validate_integer_range({"size": 11}, "size", 1, 10)
        is_valid, errors, parsed_data = validator.is_valid()
        assert not is_valid
        assert "size" in errors
