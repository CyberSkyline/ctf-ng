"""
/plugin/tests/unit/test_validators.py
Sanity checks for validation utilities
"""


class TestValidators:
    """Tests for validation utilities."""

    def test_validation_error_message_templates(self):
        """Check that ValidationError message templates format correctly."""
        from plugin.utils.validators import ValidationError

        message = ValidationError.FIELD_REQUIRED.format(field="Team Name")
        assert "Team Name" in message
        assert "required" in message.lower()

        range_message = ValidationError.FIELD_OUT_OF_RANGE.format(field="Size", min_val=1, max_val=8)
        assert "Size" in range_message
        assert "1" in range_message
        assert "8" in range_message
