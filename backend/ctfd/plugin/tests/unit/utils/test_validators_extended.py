"""
/backend/ctfd/plugin/tests/unit/utils/test_validators_extended.py
Extended unit tests for validators covering edge cases.
"""

from datetime import datetime, timedelta
from plugin.utils import (
    BaseValidator,
)


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

        invalid_datetimes = [
            "not a datetime",
            "2024/12/25",
            "25-12-2024",
            "2024-13-01T00:00:00",
            "2024-12-32T00:00:00",
            "2024-12-25T25:00:00",
            "",
        ]

        for invalid_dt in invalid_datetimes:
            dt = validator.validate_datetime({"time": invalid_dt}, "time")
            assert dt is None
            assert "time" in validator.errors
            validator.errors.clear()

    def test_datetime_past_validation(self):
        """Test datetime validation for past dates."""
        validator = BaseValidator()

        past_time = (datetime.utcnow() - timedelta(days=1)).isoformat()
        future_time = (datetime.utcnow() + timedelta(days=1)).isoformat()

        # Allow past dates
        dt = validator.validate_datetime({"time": past_time}, "time", allow_past=True)
        assert dt is not None

        # Disallow past dates
        validator.errors.clear()
        dt = validator.validate_datetime({"time": past_time}, "time", allow_past=False)
        assert dt is None
        assert "time" in validator.errors
        assert "past" in validator.errors["time"].lower()

        # Future dates always allowed
        validator.errors.clear()
        dt = validator.validate_datetime({"time": future_time}, "time", allow_past=False)
        assert dt is not None


class TestPositiveIntegerEdgeCases:
    """Test positive integer validation edge cases."""

    def test_positive_integer_edge_values(self):
        """Test edge values for positive integer validation."""
        validator = BaseValidator()

        result = validator.validate_positive_integer({"num": 0}, "num")
        assert result is None
        assert "num" in validator.errors
        assert "positive" in validator.errors["num"].lower()

        validator.errors.clear()
        result = validator.validate_positive_integer({"num": -1}, "num")
        assert result is None
        assert "num" in validator.errors

        validator.errors.clear()
        result = validator.validate_positive_integer({"num": 5.0}, "num")
        assert result == 5

        validator.errors.clear()
        result = validator.validate_positive_integer({"num": 5.7}, "num")
        assert result == 5

        validator.errors.clear()
        result = validator.validate_positive_integer({"num": 999999999}, "num")
        assert result == 999999999

    def test_positive_integer_invalid_types(self):
        """Test positive integer validation with invalid types."""
        validator = BaseValidator()

        invalid_values = [
            "not a number",
            "123abc",
            [1, 2, 3],
            {"value": 5},
        ]

        for invalid in invalid_values:
            validator.errors.clear()
            result = validator.validate_positive_integer({"num": invalid}, "num")
            assert result is None
            assert "num" in validator.errors

        validator.errors.clear()
        result = validator.validate_positive_integer({"num": None}, "num", required=False)
        assert result is None
        assert len(validator.errors) == 0

        validator.errors.clear()
        result = validator.validate_positive_integer({"num": True}, "num")
        assert result == 1

        validator.errors.clear()
        result = validator.validate_positive_integer({"num": False}, "num")
        assert result is None
        assert "num" in validator.errors


class TestStringValidationUnicode:
    """Test string validation with unicode and edge cases."""

    def test_string_length_validation_unicode(self):
        """Test string length validation with unicode characters."""
        validator = BaseValidator()

        unicode_strings = [
            "Hello 👋 World",
            "你好世界",
            "🚀🚀🚀",
            "Café ☕",
            "النص العربي",
        ]

        for test_str in unicode_strings:
            validator.errors.clear()
            valid = validator.validate_string({"text": test_str}, "text", max_length=50)
            assert valid
            assert len(validator.errors) == 0

        emoji_str = "🚀" * 10  # 10 emoji's
        validator.errors.clear()
        valid = validator.validate_string({"text": emoji_str}, "text", max_length=11)
        assert valid

        validator.errors.clear()
        valid = validator.validate_string({"text": emoji_str}, "text", max_length=9)
        assert not valid
        assert "text" in validator.errors

    def test_string_whitespace_handling(self):
        """Test string validation with various whitespace."""
        validator = BaseValidator()

        whitespace_strings = [" ", "   ", "\t", "\n", "\r\n", " \t \n "]

        for ws in whitespace_strings:
            validator.errors.clear()
            valid = validator.validate_string({"text": ws}, "text", required=True)
            assert not valid
            assert "text" in validator.errors

        validator.errors.clear()
        valid = validator.validate_string({"text": "  valid content  "}, "text", required=True)
        assert valid


class TestBooleanValidation:
    """Test boolean validation edge cases."""

    def test_boolean_validation_string_inputs(self):
        """Test boolean validation with string representations."""
        validator = BaseValidator()

        string_bools = ["true", "false", "True", "False", "1", "0", "yes", "no"]

        for str_bool in string_bools:
            validator.errors.clear()
            result = validator.validate_boolean({"flag": str_bool}, "flag")
            assert result is None
            assert "flag" in validator.errors
            assert "true or false" in validator.errors["flag"]

    def test_boolean_validation_proper_types(self):
        """Test boolean validation with proper boolean types."""
        validator = BaseValidator()

        result = validator.validate_boolean({"flag": True}, "flag")
        assert result is True

        validator.errors.clear()
        result = validator.validate_boolean({"flag": False}, "flag")
        assert result is False

        validator.errors.clear()
        result = validator.validate_boolean({"flag": None}, "flag", required=False)
        assert result is None
        assert len(validator.errors) == 0


class TestConfirmationValidation:
    """Test confirmation validation."""

    def test_confirmation_validation_case_sensitivity(self):
        """Test that confirmation is case-sensitive."""
        validator = BaseValidator()

        required_value = "DELETE ALL DATA"

        valid = validator.validate_confirmation({"confirm": "DELETE ALL DATA"}, required_value)
        assert valid

        validator.errors.clear()
        valid = validator.validate_confirmation({"confirm": "delete all data"}, required_value)
        assert not valid
        assert "confirmation" in validator.errors

        validator.errors.clear()
        valid = validator.validate_confirmation({"confirm": " DELETE ALL DATA "}, required_value)
        assert not valid


class TestIntegerRangeValidation:
    """Test integer range validation."""

    def test_integer_range_boundaries(self):
        """Test integer validation at range boundaries."""
        validator = BaseValidator()

        result = validator.validate_integer_range({"size": 1}, "size", 1, 10)
        assert result == 1

        validator.errors.clear()
        result = validator.validate_integer_range({"size": 10}, "size", 1, 10)
        assert result == 10

        validator.errors.clear()
        result = validator.validate_integer_range({"size": 0}, "size", 1, 10)
        assert result is None
        assert "size" in validator.errors
        assert "positive" in validator.errors["size"] or "between" in validator.errors["size"]

        validator.errors.clear()
        result = validator.validate_integer_range({"size": 11}, "size", 1, 10)
        assert result is None
        assert "size" in validator.errors
