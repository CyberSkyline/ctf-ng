"""
Test cases for validate_model_id functionality.
"""

import pytest

from ....challenge.models import Challenge
from ....core.utils.validator import BaseValidator


class TestValidateModelId:
    """Test the validate_model_id function."""

    def test_validate_model_id_invalid_type(self):
        """Test that non-integer values fail validation."""
        validator = BaseValidator()
        data = {"challenge_id": "not_a_number"}
        validator.validate_model_id(data, "challenge_id", "Challenge", required=True)

        assert "challenge_id" in validator.errors
        assert "must be a valid number" in validator.errors["challenge_id"]

    def test_validate_model_id_negative_number(self):
        """Test that negative numbers fail validation."""
        validator = BaseValidator()
        data = {"challenge_id": -1}
        validator.validate_model_id(data, "challenge_id", "Challenge", required=True)

        assert "challenge_id" in validator.errors
        assert "must be a valid number" in validator.errors["challenge_id"]

    def test_validate_model_id_zero(self):
        """Test that zero fails validation."""
        validator = BaseValidator()
        data = {"challenge_id": 0}
        validator.validate_model_id(data, "challenge_id", "Challenge", required=True)

        assert "challenge_id" in validator.errors
        assert "must be a valid number" in validator.errors["challenge_id"]

    def test_validate_model_id_non_existent_id(self, challenge):
        """Test that non-existent IDs fail validation."""
        validator = BaseValidator()
        data = {"challenge_id": 999999}  # Very high ID that shouldn't exist
        validator.validate_model_id(data, "challenge_id", "Challenge", required=True)

        assert "challenge_id" in validator.errors
        assert "does not exist" in validator.errors["challenge_id"]

    def test_validate_model_id_valid_id(self, challenge):
        """Test that valid IDs pass validation and return the ID."""
        validator = BaseValidator()
        data = {"challenge_id": challenge.id}
        validator.validate_model_id(data, "challenge_id", "Challenge", required=True)

        assert "challenge_id" not in validator.errors
        assert "challenge_id" in validator.parsed_data
        # Should store the ID (integer), not the Challenge object
        assert isinstance(validator.parsed_data["challenge_id"], int)
        assert validator.parsed_data["challenge_id"] == challenge.id

    def test_validate_model_id_optional_missing(self):
        """Test that optional model_id fields can be missing."""
        validator = BaseValidator()
        data = {}
        validator.validate_model_id(data, "challenge_id", "Challenge", required=False)

        assert "challenge_id" not in validator.errors
        assert "challenge_id" not in validator.parsed_data

    def test_validate_model_id_optional_none(self):
        """Test that optional model_id fields can be None."""
        validator = BaseValidator()
        data = {"challenge_id": None}
        validator.validate_model_id(data, "challenge_id", "Challenge", required=False)

        assert "challenge_id" not in validator.errors
        assert "challenge_id" not in validator.parsed_data

    def test_validate_model_id_custom_friendly_name(self):
        """Test that custom friendly names are used in error messages."""
        validator = BaseValidator()
        data = {"challenge_id": "invalid"}
        validator.validate_model_id(data, "challenge_id", "Challenge", required=True, friendly_name="Custom Challenge")

        assert "challenge_id" in validator.errors
        assert "Custom Challenge must be a valid number" == validator.errors["challenge_id"]

    def test_validate_model_id_unknown_model(self):
        """Test that unknown model names fail gracefully."""
        validator = BaseValidator()
        data = {"some_id": 1}
        validator.validate_model_id(data, "some_id", "UnknownModel", required=True)

        assert "some_id" in validator.errors
        assert "unknown model" in validator.errors["some_id"].lower()

    def test_validate_model_id_with_table_name_mapping(self, challenge):
        """Test that model name to table name mapping works."""
        validator = BaseValidator()
        data = {"challenge_id": challenge.id}

        # Test with mapped model name
        validator.validate_model_id(data, "challenge_id", "Challenge", required=True)
        assert "challenge_id" not in validator.errors
        assert isinstance(validator.parsed_data["challenge_id"], int)
        assert validator.parsed_data["challenge_id"] == challenge.id
