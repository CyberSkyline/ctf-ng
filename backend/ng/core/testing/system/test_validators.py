"""
Tests for validation utility functions
/backend/ng/core/testing/system/test_validators.py
"""

from ...utils import (
    validate_team_creation,
    validate_event_creation,
    BaseValidator,
)


class TestTeamValidation:
    """Test team creation validation."""

    def test_valid_team_creation(self):
        """Test that valid team data passes validation."""
        valid_data = {"name": "Team Alpha", "event_id": 1, "ranked": True}

        is_valid, errors = validate_team_creation(valid_data)
        assert is_valid, f"Valid data should pass but got errors: {errors}"

    def test_invalid_team_creation(self):
        """Test that invalid team data fails validation."""
        invalid_cases = [
            {"event_id": 1},  # Missing name
            {"name": ""},  # Empty name
            {"name": "Team", "event_id": "invalid"},
            {"name": "A" * 129, "event_id": 1},
        ]

        for data in invalid_cases:
            is_valid, errors = validate_team_creation(data)
            assert not is_valid, f"Invalid data should fail but passed: {data}"


class TestEventValidation:
    """Test event creation validation."""

    def test_valid_event_creation(self):
        """Test that valid event data passes validation."""
        valid_data = {
            "name": "CTF Championship",
            "description": "Annual competition",
            "max_team_size": 4,
            "locked": False,
        }

        is_valid, result = validate_event_creation(valid_data)

        assert is_valid is True, f"Valid data should pass but got errors: {result}"

        assert isinstance(result, dict)
        assert result.get("name") == "CTF Championship"
        assert result.get("max_team_size") == 4


class TestBaseValidator:
    """Test the base validator functionality."""

    def test_validate_string(self):
        """Test string validation."""
        validator = BaseValidator()

        result = validator.validate_string({"name": "Valid"}, "name", max_length=10, required=True)
        assert result is True

        result = validator.validate_string({"name": "Too long"}, "name", max_length=5, required=True)
        assert result is False
        assert "name" in validator.errors

    def test_validate_positive_integer(self):
        """Test positive integer validation."""
        validator = BaseValidator()

        result = validator.validate_positive_integer({"num": 5}, "num", required=True)
        assert result == 5

        result = validator.validate_positive_integer({"num": -1}, "num", required=True)
        assert result is None
        assert "num" in validator.errors
