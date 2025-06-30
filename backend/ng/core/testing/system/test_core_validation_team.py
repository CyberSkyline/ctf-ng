"""
Tests for team domain validation
"""

import pytest
from ...validation import BaseValidator


class ValidationError(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors or {}
        super().__init__(message)


def validate_team_creation(data):
    validator = BaseValidator()
    validator.validate_string(data, "name", max_length=128, required=True, friendly_name="Team name")
    validator.validate_positive_integer(data, "event_id", required=True, friendly_name="Event ID")

    if "ranked" in data:
        validator.parsed_data["ranked"] = data["ranked"]

    is_valid, errors, parsed_data = validator.is_valid()
    if not is_valid:
        raise ValidationError("Validation failed", errors)
    return parsed_data


class TestTeamValidation:
    """Test team creation validation."""

    def test_valid_team_creation(self):
        """Test that valid team data passes validation."""
        valid_data = {"name": "Team Alpha", "event_id": 1, "ranked": True}

        result = validate_team_creation(valid_data)
        assert result["name"] == "Team Alpha"
        assert result["event_id"] == 1
        assert result["ranked"] is True

    def test_invalid_team_creation(self):
        """Test that invalid team data fails validation."""
        invalid_cases = [
            {"event_id": 1},
            {"name": ""},
            {"name": "Team", "event_id": "invalid"},
            {"name": "A" * 129, "event_id": 1},
        ]

        for data in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                validate_team_creation(data)
            assert hasattr(exc_info.value, "errors")
            assert len(exc_info.value.errors) > 0
